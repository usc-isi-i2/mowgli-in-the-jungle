import numpy as np
import os
import json
import pickle
import sys
import pkgutil


import mowgli.classes as classes
import mowgli.parser_config as config
import mowgli.utils.general as utils

################## Utility functions #######################

def _part_a(item):
    if 'ctx_a' not in item:
        return item['ctx']
    if 'ctx' not in item:
        return item['ctx_a']
    if len(item['ctx']) == len(item['ctx_a']):
        return item['ctx']
    return item['ctx_a']

def _part_bs(item):
    if ('ctx_b' not in item) or len(item['ctx_b']) == 0:
        return ''
    else:
        return item['ctx_b']

def compose_hs_question(item):

    p1=item['activity_label']
    p2=_part_a(item)
    p3=_part_bs(item)

    return [p1, p2, p3]

def combine_siqa_answers(item, offset):
    return ['']*offset + [item['answerA'], item['answerB'], item['answerC']]

def combine_piqa_answers(item, offset):
    return ['']*offset + [item['sol1'], item['sol2']]

def combine_anli_answers(item, offset):
    return ['']*offset + [item['hyp1'], item['hyp2']]

#################### PARSERS ###########################

def prepare_anli_dataset(inputdir, dataname, max_rows=None):
    config_data=config.cfg['anli']

    # Load dataset examples
    dataset=classes.Dataset(dataname)

    offset=config_data['answer_offset']

    for split in config.parts:
        input_file='%s/%s' % (inputdir, config_data[f'{split}_input_file'])
        labels_file='%s/%s' % (inputdir, config_data[f'{split}_labels_file'])
        labels=utils.load_predictions(labels_file)

        input_data = pkgutil.get_data('mowgli', input_file).decode()
        rows=input_data.split('\n')
        for index, l in enumerate(rows):
            if max_rows and index>=max_rows: break
            if l:
                item = json.loads(l)
                split_data=getattr(dataset, split)
                an_entry=classes.Entry(
                    split=split,
                    id='{}-{}'.format(split, item["story_id"]),
                    question=[item['obs1'], item['obs2']],
                    answers=combine_anli_answers(item, offset),
                    correct_answer=None if split == 'test' else labels[index]
                )
                split_data.append(an_entry)
    return dataset

def prepare_hellaswag_dataset(inputdir, dataname, max_rows=None):
    config_data=config.cfg['hellaswag']

    # Load dataset examples
    dataset=classes.Dataset(dataname)

    offset=config_data['answer_offset']

    for split in config.parts:
        input_file='%s/%s' % (inputdir, config_data[f'{split}_input_file'])
        labels_file='%s/%s' % (inputdir, config_data[f'{split}_labels_file'])
        labels=utils.load_predictions(labels_file)

        input_data = pkgutil.get_data('mowgli', input_file).decode()
        rows=input_data.split('\n')
        for index, l in enumerate(rows):
            if max_rows and index>=max_rows: break
            if l:
                item = json.loads(l)
                split_data=getattr(dataset, split)
                an_entry=classes.Entry(
                    split=split,
                    id='{}-{}'.format(split, item['ind']),
                    question=compose_hs_question(item),
                    answers=['']*offset + item['ending_options'],
                    correct_answer=None if split == 'test' else labels[index],
                    metadata={'activity_label': item['activity_label'], 'dataset': item['dataset'], 'split_type': item['split_type']}
                )
                split_data.append(an_entry)
    return dataset

def prepare_socialiqa(inputdir, dataname, max_rows=None):
    config_data=config.cfg['socialiqa']

    # Load dataset examples
    dataset=classes.Dataset(dataname)

    offset=config_data['answer_offset']

    for split in config.parts:
        input_file='%s/%s' % (inputdir, config_data[f'{split}_input_file'])
        labels_file='%s/%s' % (inputdir, config_data[f'{split}_labels_file'])
        labels=utils.load_predictions(labels_file)

        input_data = pkgutil.get_data('mowgli', input_file).decode()
        rows=input_data.split('\n')
        for index, l in enumerate(rows):
            if max_rows and index>=max_rows: break
            if l:
                item = json.loads(l)
                split_data=getattr(dataset, split)
                an_entry=classes.Entry(
                    split=split,
                    id='{}-{}'.format(split, index),
                    question=[item['context'], item['question']],
                    answers=combine_siqa_answers(item, offset),
                    correct_answer=None if split == 'test' else labels[index]
                )
                split_data.append(an_entry)
    return dataset

def prepare_physicaliqa(inputdir, dataname, max_rows=None):
    config_data=config.cfg['physicaliqa']

    # Load dataset examples
    dataset=classes.Dataset(dataname)

    offset=config_data['answer_offset']

    for split in config.parts:
        input_file='%s/%s' % (inputdir, config_data[f'{split}_input_file'])
        labels_file='%s/%s' % (inputdir, config_data[f'{split}_labels_file'])
        labels=utils.load_predictions(labels_file)

        input_data = pkgutil.get_data('mowgli', input_file).decode()
        rows=input_data.split('\n')
        for index, l in enumerate(rows):
            if l:
                if max_rows and index>=max_rows: break
                item = json.loads(l)
                split_data=getattr(dataset, split)
                an_entry=classes.Entry(
                    split=split,
                    id='{}-{}'.format(split, item['id']),
                    question=[item['goal']],
                    answers=combine_piqa_answers(item, offset),
                    correct_answer=None if split == 'test' else labels[index]
                )
                split_data.append(an_entry)
    return dataset

def parse_se_question(question, instance_id, context, split):
    q_text=question['@text']
    q_id=question['@id']
    correct_answer=-1
    answers=[]
    for answer in question['answer']:
        a_text=answer['@text']
        answers.append(a_text)
        if answer["@correct"]=='True':
            correct_answer=answer["@id"]
    an_entry=classes.Entry(
            split=split,
            id='{}-{}-{}'.format(split, instance_id, q_id),
            question=[context, q_text],
            answers=answers,
            correct_answer=correct_answer)
    return an_entry

def prepare_semeval2018(inputdir, dataname, max_rows=None):
    config_data=config.cfg['se2018t11']
    # Load dataset examples
    dataset=classes.Dataset(dataname)

    offset=config_data['answer_offset']
    
    for split in config_data['parts']:
        input_file='%s/%s' % (inputdir, config_data[f'{split}_input_file'])

        input_data = json.loads(pkgutil.get_data('mowgli', input_file).decode())
        instances=input_data['data']['instance']

        i=0
        for instance in instances:
            if max_rows and i>=max_rows: break
            instance_id=instance['@id']
            context=instance['text']
            if instance['questions']:
                questions=instance['questions']['question']
                if isinstance(questions, list):
                    for question in questions:
                        an_entry=parse_se_question(question, instance_id, context, split)
                        split_data=getattr(dataset, split)
                        split_data.append(an_entry)
                        i+=1
                        if max_rows and i>=max_rows: break
                else:
                    an_entry=parse_se_question(questions, instance_id, context, split)
                    split_data=getattr(dataset, split)
                    split_data.append(an_entry)
                    i+=1
                    if max_rows and i>=max_rows: break
    return dataset

    

def parse_dataset(datadir, name, max_rows=None):
    if name.startswith('anli') or name.startswith('alphanli'):
        return prepare_anli_dataset(datadir, name, max_rows)
    elif name.startswith('hellaswag') or name.startswith('hs'):
        return prepare_hellaswag_dataset(datadir, name, max_rows)
    elif name.startswith('physicaliqa') or name.startswith('piqa'):
        return prepare_physicaliqa(datadir, name, max_rows)
    elif name.startswith('socialiqa') or name.startswith('siqa'):
        return prepare_socialiqa(datadir, name, max_rows)
    elif name.startswith('se2018') or name.startswith('semeval'):
        return prepare_semeval2018(datadir, name, max_rows)
    else:
        return 'Error: dataset name does not exist!'
