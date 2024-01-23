from .lexical import LexicalNER
from .ngrams import NGramNER
from app.services.cso_ner import CSONER
from threading import Thread

class NamedEntityRecognition:
    def __init__(self, text):
        self.text = text

    def get_entities(self):
        '''
        Gets the named entities from different techniques in parallel
        '''
        results = {}
        threads = []

        def from_lexical_ner():
            results['lexical_ne'] = LexicalNER(self.text).get_entities()

        def from_csoner():
            results['model_ne'] = CSONER(self.text).get_entities()

        threads.append(Thread(target=from_lexical_ner))
        # threads.append(Thread(target=from_ngram_ner))
        threads.append(Thread(target=from_csoner))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return set(results['lexical_ne'] + results['model_ne'])