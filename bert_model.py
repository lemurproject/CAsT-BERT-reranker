import torch
from transformers import BertModel, BertConfig
from transformers import BertTokenizer
from transformers import DistilBertTokenizer, DistilBertModel
from pdb import set_trace as bp

class BertRank(torch.nn.Module):

    def __init__(self, args):

        super(BertRank, self).__init__()

        self.args = args

        if self.args.bert_type == "base":
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', \
                do_lower_case=True)
            self.bert = BertModel.from_pretrained('bert-base-uncased')

        if self.args.bert_type == "distil":
            self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-cased', \
                do_lower_case=True)
            self.bert = DistilBertModel.from_pretrained('distilbert-base-cased')

        self.class_layer = torch.nn.Linear(768, 2)

        self.dropout = torch.nn.Dropout(args.dropout)

    def get_input(self, examples):

        tokenised_examples = []
        lengths = []

        max_length = 0
        for each in examples:

            tokenised_query = self.tokenizer.tokenize((each[0]))
            tokenised_query = tokenised_query[:self.args.max_query_length]
            tokenised_query = ['[CLS'] + tokenised_query + ['[SEP']

            query_len = len(tokenised_query)

            # subtract 1 to account for end [SEP]
            allowed_pas_len = self.args.max_seq_length - 1 - query_len
            tokenised_passage = self.tokenizer.tokenize((each[1]))
            tokenised_passage = tokenised_passage[:allowed_pas_len]
            tokenised_passage = tokenised_passage + ['[SEP]']
            
            pass_len = len(tokenised_passage)

            max_length = max(max_length, query_len + pass_len)
            
            lengths.append([query_len, pass_len])
            tokenised_examples.append((tokenised_query, tokenised_passage))

        #print("Max Length is ", max_length)
        indexed_examples = []
        seg_mask = []
        attn_mask = []

        for each, lens in zip(tokenised_examples, lengths):

            query = each[0]
            passage = each[1]

            segs = [0] * len(query)
            segs = segs + [1] * len(passage)
            segs = segs + [1] * (max_length - sum(lens))

            final_example = query + passage
            final_example = final_example + ['[PAD]'] * (max_length - sum(lens))

            final_example = self.tokenizer.convert_tokens_to_ids(\
                    final_example)

            attn = [int(t_id > 0) for t_id in final_example]

            indexed_examples.append(final_example)
            seg_mask.append(segs)
            attn_mask.append(attn)

        indexed_examples = torch.tensor(indexed_examples).to(self.args.device)
        seg_mask = torch.tensor(seg_mask).to(self.args.device)
        attn_mask = torch.tensor(attn_mask).to(self.args.device)

        return indexed_examples, seg_mask, attn_mask

    def forward(self, examples):

        inputs, seg_mask, attn_mask = self.get_input(examples)
        # change for previous models
        #if self.args.bert_type == "base":
        outputs = self.bert(inputs, attention_mask=attn_mask,\
            token_type_ids=seg_mask)
        #if self.args.bert_type == "distil":
        #    outputs = self.bert(inputs, attention_mask=attn_mask)

        cls_output = outputs[0][:, 0]
        #cls_output = self.dropout(cls_output)
        output = self.class_layer(cls_output) 
        return output
