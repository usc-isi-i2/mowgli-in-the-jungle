from typing import List, Optional, Union, Dict, Any

import IPython
# import pytorch_lightning as pl
import lazy_import

pl = lazy_import.lazy_module('pytorch_lightning')
# import numpy as np
np = lazy_import.lazy_module('numpy')

import torch
from pytorch_lightning import Trainer
from torch import nn
import torch.utils.data
from torch.optim import AdamW

import mowgli.classes
from mowgli.predictor.PytorchLigthningPredictor import PytorchLightningPredictor
from mowgli.predictor.utils import ClassificationDataset
from mowgli.utils.LM.SentenceEmbedder import SentEmbedder
# from mowgli.utils.graphs.KGNetworkx import NxKG

import logging

logger = logging.getLogger(__name__)


class BaseLMTrainer(pl.LightningModule):
    def __init__(self, max_length: int = 128, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_sent_len = max_length
        self.LM = SentEmbedder(name='roberta-base', token_pooling='mean')

    def forward(self, tokens: Dict[str, torch.Tensor]) -> torch.Tensor:
        return self.LM(**tokens)

    def collate(self, sents):
        tokens = self.LM.tokenize(sents, max_length=self.max_sent_len)
        return tokens


class BaseLMTuner(pl.LightningModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hparams = {
            'batch_size': 4,
            'learning_rate': 2e-6,
            'adam_epsilon': 10e-8,
        }
        self.classifier: Optional[nn.Linear] = None
        self.loss: Optional[nn.Linear] = None
        self._trained_LM: Optional[BaseLMTrainer] = None

    def build(self):
        assert self.trained_LM.LM is not None

        self.classifier = nn.Linear(self.trained_LM.LM.config.hidden_size, 1, bias=True)
        self.loss = nn.CrossEntropyLoss(ignore_index=-1, reduction="mean")
        self.classifier.weight.data.normal_(mean=0.0, std=self.trained_LM.LM.config.initializer_range)
        self.classifier.bias.data.zero_()

    ##############################################################

    @property
    def trained_LM(self):
        logger.info(f'trained_LM getter')
        return self._trained_LM

    @trained_LM.setter
    def trained_LM(self, value: pl.LightningModule):
        logger.info(f'trained_LM setter')
        self._trained_LM = value

    ##############################################################

    def forward(self, batch: Dict[str, torch.Tensor]) -> torch.Tensor:
        sent_embd = self.trained_LM(batch)
        probs = self.classifier(sent_embd)
        return probs

    def configure_optimizers(self):
        optimizer = AdamW(self.parameters(), lr=float(self.hparams["learning_rate"]),
                          eps=float(self.hparams["adam_epsilon"]))

        return optimizer

    def training_step(self, batch: Dict[str, torch.Tensor], batch_idx: torch.Tensor) -> Dict[str, torch.Tensor]:
        logits = self.forward(batch)
        loss = self.loss(logits, batch["labels"])
        if self.trainer and self.trainer.use_dp:
            loss = loss.unsqueeze(0)

        return {
            "loss": loss
        }

    def validation_step(self, batch, batch_idx):
        logits = self.forward(batch)
        loss = self.loss(logits, batch["labels"])
        if self.trainer and self.trainer.use_dp:
            loss = loss.unsqueeze(0)
        return {
            'val_loss': loss,
            "val_batch_logits": logits,
            "val_batch_labels": batch["labels"],
            "batch_idx": batch_idx,
        }

    def validation_end(self, outputs):

        val_loss_mean = torch.stack([o['val_loss'] for o in outputs]).mean()
        val_logits = torch.cat([o["val_batch_logits"] for o in outputs])
        val_labels = torch.cat([o["val_batch_labels"] for o in outputs])
        self.logger.experiment.add_scalar('valid_loss', val_loss_mean)

        val_pred = torch.argmax(val_logits, dim=1)

        val_acc = torch.sum(val_labels == val_pred) / (val_labels.shape[0] * 1.0)
        self.logger.experiment.add_scalar('valid_acc', val_acc)
        logger.info(f'valid_acc={val_acc}, valid_loss={val_loss_mean}')
        return {
            'val_loss': val_loss_mean,
            "progress_bar": {
                "val_accuracy": val_acc
            }
        }

    def dataset_to_dataloader(self, inputs: List[mowgli.classes.Entry]) -> torch.utils.data.DataLoader:
        return torch.utils.data.DataLoader(
            ClassificationDataset(inputs),
            batch_size=self.hparams["batch_size"], collate_fn=self.collate
        )

    def collate(self, entries: List[mowgli.classes.Entry]) -> Dict[str, torch.Tensor]:
        sents = [e.context + e.question + a.text for e in entries for a in e.answers]

        tokens = self.trained_LM.collate(sents)

        if entries[0].correct_answer is not None:
            correct_labels = np.array([int(e.labels.index(e.correct_answer))
                                       for e in entries])
            labels = np.squeeze(
                np.eye(len(entries[0].answers))[correct_labels.reshape(-1)]
            ).reshape([-1])
            labels = {'labels': labels}
        else:
            labels = {}
        return {
            **tokens,
            **labels
        }


class BaseLMPredictor(PytorchLightningPredictor):
    def __init__(self, max_length: int = 128, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._train_pl_module: pl.LightningModule = BaseLMTrainer(max_length=max_length)
        self._tune_pl_module: pl.LightningModule = BaseLMTuner()

    #################################################################

    @property
    def train_pl_module(self):
        logger.info(f'train_pl_module getter')
        return self._train_pl_module

    @train_pl_module.setter
    def train_pl_module(self, m):
        logger.info(f'train_pl_module setter')
        self._train_pl_module = m

    @property
    def tune_pl_module(self):
        logger.info(f'tune_pl_module getter')
        return self._tune_pl_module

    @tune_pl_module.setter
    def tune_pl_module(self, m):
        logger.info(f'tune_pl_module setter')
        self._tune_pl_module = m

    #################################################################

    def train(self, config) -> Any:
        logger.info(f'No training to do here!1')
        self.tune_pl_module._trained_LM = self.train_pl_module

    def preprocess(self, dataset: mowgli.classes.Dataset, config: Any) -> Any:
        logger.info(f'No preprocess to do here!')

    def tune(self, dataset: mowgli.classes.Dataset, config: Any) -> Any:
        self.tune_pl_module.build()
        trainer = Trainer(
            gradient_clip_val=0,
            num_nodes=1,
            gpus=config['gpus'],
            show_progress_bar=True,
            accumulate_grad_batches=config["accumulate_grad_batches"],
            max_epochs=config["max_epochs"],
            min_epochs=1,
            val_check_interval=0.25,
            weights_summary='top',
            num_sanity_val_steps=5,
            resume_from_checkpoint=None,
        )
        train_loader = self.tune_pl_module.dataset_to_dataloader(dataset.train)
        eval_loader = self.tune_pl_module.dataset_to_dataloader(dataset.dev)
        trainer.fit(self.tune_pl_module,
                    train_dataloader=train_loader,
                    val_dataloaders=eval_loader)

    def predict(self, model: Any, dataset: mowgli.classes.Dataset, config: Any = None, partition: str = 'test') -> List:
        """

        Args:
            model:
            dataset:
            config:
            partition:

        Returns:

        """
        IPython.embed()

        dataloader = self.tune_pl_module.dataset_to_dataloader(getattr(dataset, partition))
        trainer = Trainer(
            gradient_clip_val=0,
            num_nodes=1,
            gpus=config['gpus'],
            show_progress_bar=True,
            accumulate_grad_batches=config["accumulate_grad_batches"],
            max_epochs=config["max_epochs"],
            min_epochs=1,
            val_check_interval=0.25,
            weights_summary='top',
            num_sanity_val_steps=5,
            resume_from_checkpoint=None,
        )
        trainer.test(self.tune_pl_module, test_dataloaders=dataloader)
