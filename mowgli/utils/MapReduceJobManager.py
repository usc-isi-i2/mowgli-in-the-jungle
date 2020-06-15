import sys
import multiprocessing as mp
import typing
import functools
import dill

from loguru import logger
import queue
import tqdm
import time

def dill_wrapper(all_dill):
    func, dill_kwargs = dill.loads(all_dill)
    args, kwargs = dill.loads(dill_kwargs)
    logger.debug(f'arguments after dill: {(args, kwargs)}')
    return func(*args, **kwargs)


def run_with_timeout(func: typing.Callable[[typing.Any], typing.Any], max_timeout: int = -1,
                     args: typing.Tuple=(), kwargs:typing.Dict[str, typing.Any]={}):

    if max_timeout <= 0:
        return func(*args, **kwargs)

    with mp.Pool(1) as p:
        logger.debug(f'arguments for dill: {(args, kwargs)}')
        dill_kwargs = dill.dumps((args, kwargs))
        all_dill = dill.dumps((func, dill_kwargs))
        out = p.apply_async(dill_wrapper, (all_dill,))
        # out = p.apply_async(submit_func=submit_func, args=args, kwds=kwargs)
        return out.get(timeout=max_timeout)


class HashableDict(dict):
    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


class MapReduceJobManager:
    def __init__(self, n_worker:int=10, timeout:int=5):

        self.n_workers: int = n_worker
        self.timeout: int = timeout

        self.args_q = mp.Queue(maxsize=n_worker*2)
        self.return_q = mp.Queue(maxsize=n_worker*2)

        self.workers: typing.List[mp.Process] = []

        self.initialized:bool = False

        self.n_ongoing: int = 0

    def start_workers(self, func: typing.Callable,
                      pre_func: typing.Callable[[], typing.Dict] = None) \
            -> typing.NoReturn:
        logger.info(f'master is starting workers')
        self.workers = [mp.Process(target=MapReduceJobManager.__worker_container,
                                   args=(func, pre_func, self.args_q, self.return_q, self.timeout))
                        for _ in range(self.n_workers)]

        [w.start() for w in self.workers]

        self.initialized = True

    @staticmethod
    def __worker_container(func: typing.Callable,
                           pre_func: typing.Callable[[], typing.Dict[str, typing.Any]],
                           args_q: mp.Queue, return_q:mp.Queue, timeout:int=-1) \
        -> typing.NoReturn:

        WAIT_TIME_M = 5

        me = f'{mp.current_process()} |'

        logger.info(me+'worker started')

        if pre_func is not None:
            logger.info(me+f'running pre_func {pre_func}')
            pre_output: typing.Dict[str, typing.Any] = pre_func()
            logger.debug(me + f'pre_func output keys {pre_output.keys()}')
        else:
            pre_output = {}

        logger.info(me+f'worker setup is done')
        while True:
            logger.debug(me+f'Waiting for new job ...')
            try:
                args, kwargs = args_q.get(block=True, timeout=WAIT_TIME_M*60)
            except TimeoutError:
                logger.debug(me+'Still waiting for any job')
                raise
            except queue.Empty:
                logger.debug(me + 'args queue is empty')
                time.sleep(10)
                continue

            assert isinstance(kwargs, HashableDict), me + f'argument is not hashabledict'

            job_id = MapReduceJobManager.__job_hash(args, kwargs)
            try:
                kwargs_with_pre = HashableDict({**kwargs, **pre_output})
                logger.debug(me +f'Got a new job {job_id}')
                output = run_with_timeout(func=func, max_timeout=timeout,
                                          args=args, kwargs=kwargs_with_pre)
                logger.debug(me + f'Job finished {job_id}')
            except mp.context.TimeoutError:
                logger.warning(me +f'Job timed out {job_id}')
                output = None
            except:
                logger.exception(me + f'Job Failed {job_id}, with error {sys.exc_info()[0]}')
                output = None

            logger.debug(me +f'Commiting job {job_id}')

            try:
                return_q.put( ((args, kwargs),output) , timeout=WAIT_TIME_M*60)
            except TimeoutError:
                logger.error(me + 'return queue not responding')
                return None

    def push_job(self, *args, **kwargs) -> typing.NoReturn:

        assert isinstance(kwargs, dict), f'input is not dict'
        job_kwargs = HashableDict(kwargs)
        logger.info(f'master pushing job {MapReduceJobManager.__job_hash(args, job_kwargs)}')

        self.args_q.put((*args,job_kwargs))
        self.n_ongoing += 1

    def pull_result(self) -> typing.Tuple[typing.Tuple[typing.Tuple, typing.Dict], typing.Any]:
        (args, kwargs),output = self.return_q.get()
        logger.info(f'master got result {MapReduceJobManager.__job_hash(args, kwargs)}')
        self.n_ongoing -= 1
        return (args, kwargs),output

    def mapper(self, args_list: typing.List[typing.Union[typing.Tuple, typing.Any]] = None,
               kwargs_list: typing.List[typing.Dict[str, typing.Any]] = None) \
            -> typing.List[typing.Any]:
        assert self.initialized, f'I am not initialized, run start_workers'

        if args_list is not None and kwargs_list is not None:
            assert len(args_list) == len(kwargs_list), (
                f'inconsistent arguments size {len(args_list)} != {len(kwargs_list)}')
        
        jobs = iter(zip(args_list, kwargs_list))
        
        pull_remaining = len(args_list)
        
        def push_chunk():
            num = 0
            for _ in range(self.n_workers):
                try:
                    args, kwargs = jobs.__next__()
                except StopIteration:
                    break
                num += 1
                if not isinstance(args, tuple):
                    args = (args,)
                self.push_job(args, **kwargs)
            return num

        results = []
        push_remaining = pull_remaining
        logger.info(f'Total number of jobs: {push_remaining}')
        
        if push_remaining > 2*self.n_workers:
            p1 = push_chunk()
            p2 = push_chunk()
            push_remaining -= (p1 + p2)
        
        pbar = tqdm.tqdm(total=pull_remaining)
        
        def pull_one():
            logger.debug(f'master waiting for results')
            out = self.pull_result()
            logger.debug(f'master got results')
            results.append(out)
        
        while push_remaining > 0:
            p1 = push_chunk()
            push_remaining -= p1

            # get chunk
            for _ in range(self.n_workers):
                pull_one()
                pbar.update(1)
                pull_remaining -= 1
        
        while pull_remaining > 0:
            pull_one()
            pbar.update(1)
            pull_remaining -= 1
        
        assert pull_remaining == 0, f'pull_remaining is not zero, {pull_remaining}'
        assert push_remaining == 0, f'push_remaining is not zero, {push_remaining}'
        
        return results

    @staticmethod
    def map(func: typing.Callable,
            args_list: typing.List[typing.Union[typing.Tuple, typing.Any]] = None,
            kwargs_list: typing.List[typing.Dict[str, typing.Any]] = None,
            pre_func: typing.Callable[[], typing.Dict] = None, 
            n_worker: int = mp.cpu_count(),
            timeout: int = -1):

        m = None
        ###########################################
        from collections import OrderedDict
        d = OrderedDict()
        if args_list is None:
            args_list = [()]*len(kwargs_list)
        elif kwargs_list is None:
            kwargs_list = [HashableDict()] * len(args_list)
        for (_arg, _kwarg) in zip(args_list, kwargs_list):
            k = MapReduceJobManager.__job_hash(_arg, HashableDict(_kwarg))
            d[k] = None
        ###########################################
        print(f'running map for {len(args_list)} jobs')
        ###########################################
        try:
            m = MapReduceJobManager(n_worker, timeout=timeout)
            m.start_workers(func=func, pre_func=pre_func)

            results = m.mapper(args_list, kwargs_list)
        except Exception as e:
            logger.error(e)
            raise e
        finally:
            if m is not None:
                m.kill()
        ###########################################
        for ((ar, kwar), out) in results:
            k = MapReduceJobManager.__job_hash(ar, kwar)
            d[k] = out
        
        return [v for k, v in d.items()]

    @staticmethod
    def __job_hash(args, job_kwargs):
        return hash((*args, job_kwargs))

    def kill(self):
        logger.info(f'Killing the job manager')
        for w in self.workers:
            if w is not None:
                w.terminate()

