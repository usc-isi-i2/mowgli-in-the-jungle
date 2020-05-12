from typing import List, Dict

import torch
from transformers import AutoModel, AutoTokenizer
import pathlib

# MYPATH = pathlib.PurePath('/nas/home/qasemi/STMCS/Utils/LM')
MYPATH = pathlib.PurePath('/nas/home/qasemi')


class SentEmbedder(torch.nn.Module):
    def __init__(self, tuned_path: str = None, name: str = None, token_pooling: str = ""):

        super().__init__()
        assert token_pooling in ['last', 'mean', 'max', 'cls'], f'Invalid pooling method: {token_pooling}'
        self.token_pool = token_pooling

        assert (tuned_path is None) != (name is None), f'One of them must be None, {tuned_path}, {name}'
        if tuned_path is not None:
            tuned_path = str(pathlib.Path(tuned_path).expanduser())
            self.embedder = AutoModel.from_pretrained(tuned_path)
            self.tokenizer = AutoTokenizer.from_pretrained(tuned_path, use_fast=False)
        elif name is not None:
            self.embedder = AutoModel.from_pretrained(name, cache_dir=MYPATH/"model_cache")
            self.tokenizer = AutoTokenizer.from_pretrained(name, cache_dir=MYPATH/"model_cache", use_fast=False)

        self.embedder.train()

        self.cls = self.tokenizer.cls_token + ' '

        # self.embed_size = self.embedder.config.hidden_size
        self.config = self.embedder.config

    def _get_token_embeddings(self, input_ids, attention_mask, token_type_ids=None) -> torch.Tensor:
        """
        Applies the language model as a token embedding to the given batch of tokens and returns the token embeddings
        :param input_ids:
        :param attention_mask:
        :param token_type_ids:
        :return:
        """
        assert len(input_ids.shape) == 2, "LM only take two-dimensional input"
        assert len(attention_mask.shape) == 2, "LM only take two-dimensional input"
        assert len(token_type_ids.shape) == 2, "LM only take two-dimensional input"

        token_type_ids = None if "roberta" in str(self.embedder.__class__) else token_type_ids

        results = self.embedder(input_ids=input_ids, attention_mask=attention_mask,
                                token_type_ids=token_type_ids)

        token_embeddings, *_ = results

        return token_embeddings

    def forward(self, **kwargs) -> torch.Tensor:
        return self.get_sent_embedding(**kwargs)

    def get_sent_embedding(self, input_ids: torch.Tensor, attention_mask: torch.Tensor,
                           token_type_ids: torch.Tensor = None, input_len: torch.Tensor = None,
                           **kwargs) -> torch.Tensor:
        """
        Wraps token embedding in a set of token pooling methods to give a single vector for each sentence as embedding
        :param input_ids:
        :param attention_mask:
        :param token_type_ids:
        :param input_len:
        :param kwargs:
        :return:
        """
        if self.token_pool == 'last':
            assert input_len is not None, f'Need valid input_len for \'last\' toke pooling method'
        assert (input_len is None) or (len(input_len.shape) == 1), f'Pooling only accepts 1D input_len'
        token_embeddings = self._get_token_embeddings(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)

        if self.token_pool == 'last':
            ind = input_len - 1
            sent_embeddings = token_embeddings[torch.arange(token_embeddings.size(0)), ind]
        elif self.token_pool == 'mean':
            sent_embeddings = torch.mean(token_embeddings, dim=1)
        elif self.token_pool == 'max':
            sent_embeddings = torch.max(token_embeddings, dim=1)
        elif self.token_pool == 'cls':
            # get the second token as the sent embedding. Here we assume that the first token is 'bos_token' and
            # the second token is always 'cls_token'.
            ind = torch.ones_like(input_len)
            sent_embeddings = token_embeddings[torch.arange(token_embeddings.size(0)), ind]
        else:
            raise ValueError(f'invalid pooling method {self.token_pool}')

        return sent_embeddings

    def tokenize(self, sents: List[str], max_length: int = 128) -> Dict[str, torch.Tensor]:
        if self.token_pool == 'cls':
            sents = [self.cls + s for s in sents]
        results = self.tokenizer.batch_encode_plus(sents, add_special_tokens=True,
                                                   max_length=max_length, return_tensors='pt',
                                                   return_attention_masks=True, pad_to_max_length=True,
                                                   return_input_lengths=True, return_token_type_ids=True)
        return results