import os
import requests
from transformers import AutoTokenizer, DistilBertForTokenClassification
import torch
from app import logger

CSO_NER_DISTILBERT_PATH="storage/models/cso_ner_distilbert/"

class CSONER:
    def __init__(self, text):
        self.model = DistilBertForTokenClassification.from_pretrained(CSO_NER_DISTILBERT_PATH)
        self.tokenizer = AutoTokenizer.from_pretrained(CSO_NER_DISTILBERT_PATH)
        self.text = text
    
    def get_entities(self):
        # Tokenize the text and convert to tensors
        inputs = self.tokenizer(self.text, return_tensors="pt")

        with torch.no_grad():
            logits = self.model(**inputs).logits
        
        predicted_token_class_ids = logits.argmax(-1).squeeze().tolist()

        # Convert token ids to labels and merge consecutive tokens of the same label
        entities = []
        current_entity = None

        for idx, label_id in enumerate(predicted_token_class_ids):
            # Skip special tokens
            if idx in [0, len(predicted_token_class_ids) - 1]:
                continue

            label = self.model.config.id2label[label_id]
            if label != 'O':
                token = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0][idx].item())

                if label.startswith('B-') or (current_entity is None):
                    if current_entity:
                        entities.append(current_entity)
                    current_entity = {
                        'entity': token,
                        'label': label[2:],  # Remove 'B-' or 'I-'
                        'start': idx,
                        'end': idx
                    }
                elif label.startswith('I-') and current_entity and label[2:] == current_entity['label']:
                    current_entity['entity'] += ' ' + token
                    current_entity['end'] = idx
            else:
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None

        if current_entity:
            entities.append(current_entity)

        # Convert token back to words and adjust offsets
        for entity in entities:
            entity['entity'] = self.tokenizer.convert_tokens_to_string(entity['entity'].split())
            entity['start'] = inputs.token_to_chars(0, entity['start']).start
            entity['end'] = inputs.token_to_chars(0, entity['end']).end

        return [item['entity'] for item in entities if 'entity' in item]

        



