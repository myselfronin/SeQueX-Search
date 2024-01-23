import time
from app import logger
from .ner import NamedEntityRecognition
from .canditate_entity_generator import CandidateEntityGenerator
from .candidate_entity_disambiguator import CandidateDisambiguator

class NamedEntityDisambiguator:
    def __init__(self, processed_query):
        self.processed_query = processed_query

    def get_linked_entities(self):
        recognized_entities = self.named_entity_recognition()

        candidate_set_for_entities = self.candidate_entity_generation(recognized_entities)

        linked_entities = self.candidate_entity_disambiguation(candidate_set_for_entities, self.processed_query)

        return linked_entities

    
    def named_entity_recognition(self):
        #--------
        logger.info("Starting Named Entity Recognition")
        ner_start_time = time.time()
        #--------

        entities = NamedEntityRecognition(self.processed_query).get_entities()

        #--------
        ner_time_taken = time.time() - ner_start_time
        logger.info("NER time taken: " + str(ner_time_taken) + " seconds")

        logger.info('Recognized Entities: ' + ', '.join(entities))
        #--------

        return entities

    def candidate_entity_generation(self, recognized_entities):
        logger.info("Start Candidate Entity Generation")

        candidate_set_for_entities = CandidateEntityGenerator(recognized_entities).get_candidates()

        #--------
        self.log_candidates_set(candidate_set_for_entities)
        #--------

        return candidate_set_for_entities
    
    def candidate_entity_disambiguation(self, candidate_set_for_entities, query_context):
        disambiguator = CandidateDisambiguator(query_context, candidate_set_for_entities)
        linked_entities =  { mention: disambiguator.disambiguate(mention) for mention in candidate_set_for_entities}

        #--------
        self.log_disambiguate_entity(linked_entities)
        #--------

        return linked_entities

    def log_disambiguate_entity(self, linked_entities):
        formatted_pairs = [f"Entity Linking: '{key}': {value}" for key, value in linked_entities.items()]
        logger.info('\n' + '\n'.join(formatted_pairs))

    def log_candidates_set(self, candidate_set):
        # Create a list of formatted strings
        formatted_entries = [f"Recognized Entity: '{entity}', Candidate Entities [{len(candidates)}]: {', '.join(candidates)}" 
                            for entity, candidates in candidate_set.items()]
        # Join the formatted strings and log them
        logger.info('\n'.join(formatted_entries))



        