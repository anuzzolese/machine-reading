from abc import ABC, abstractmethod
from rdflib.graph import Graph, Dataset, URIRef
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Requires, Provides
from rdflib import store
import shortuuid
from api.api import GraphStore, Corpus

@ComponentFactory("machine-reading-consumer-factory")
@Requires('_maschine_readers', "machine-reader", aggregate=True)
@Provides("machine-reading-workflow")
@Instantiate("machine-reading-workflow-impl")
class MachineReadingConsumer(object):
    
    
    def __init__(self):
        self._maschine_readers = None
        
    @Validate
    def validate(self, context):
        shortuuid.set_alphabet("0123456789abcdefghijkmnopqrstuvwxyz")
        print(f'{len(self._maschine_readers)} machine readers available.')
        
    def process_text(self, text: str, base_namespace: str = 'https://w3id.org/stlab/', gstore: GraphStore = GraphStore()) -> GraphStore:
        
        id = shortuuid.uuid(text)[:8]
        
        for machine_reader in self._maschine_readers:
            local_namespace = f'{base_namespace}{id}/{machine_reader.get_name()}'
            g = machine_reader.read(text, namespace=f'{local_namespace}/')
            gstore.add_named_graph(g, URIRef(local_namespace))
            
        return gstore
    
    
@ComponentFactory("corpus_processor")
@Requires('_workflow', "machine-reading-workflow")
@Provides("corpus-processor")
@Instantiate("corpus-processor-impl")
class CorpusProcessor(object):
    
    
    def __init__(self):
        self._workflow = None
        
    @Validate
    def validate(self, context):
        if self._workflow:
            print('Everything ready for the running the corpus processor.')
        else:
            print('The corpus processor cannot run as the machine reading workflow is not enabled.')
        
    def process_corpus(self, corpus: Corpus, base_namespace: str = 'https://w3id.org/stlab/'):
        
        gstore = GraphStore()
        
        for text in corpus:
            self._workflow.process_text(text, base_namespace, gstore)
        
        return gstore
    
if __name__ == '__main__':
    print('stocazzo')