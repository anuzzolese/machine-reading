from abc import ABC, abstractmethod
from io import StringIO
from rdflib.graph import Graph, Dataset, URIRef
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Requires, Provides
from rdflib import store
import shortuuid
from machine_reading.api.api import GraphStore, Corpus, MachineReader
from machine_reading.api.ontology import MRO
from typing import List, Dict, Union
import csv
import uuid
import json
from threading import Thread
from builtins import callable
import pandas as pd
from rdflib.namespace import Namespace
from rdflib.namespace._RDF import RDF
from rdflib.term import Literal
from rdflib.namespace._RDFS import RDFS
from pathlib import Path




@ComponentFactory("machine-reading-consumer-factory")
@Requires('_maschine_readers', "machine-reader", aggregate=True)
@Provides("machine-reading-workflow")
@Instantiate("machine-reading-workflow-impl")
class MachineReadingConsumer(object):
    
    
    def __init__(self):
        self._maschine_readers : List[MachineReader] = None
        
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
#@Requires('_workflow', "machine-reading-workflow")
@Requires('_maschine_readers', "machine-reader", aggregate=True)
@Provides("corpus-processor")
@Instantiate("corpus-processor-impl")
class CorpusProcessor(object):
    
    __JOB_MAP = None
    
    def __init__(self):
        self._workflow = None
        
    @Validate
    def validate(self, context):
        if self._workflow:
            print('Everything ready for the running the corpus processor.')
        else:
            print('The corpus processor cannot run as the machine reading workflow is not enabled.')
            
        CorpusProcessor.__JOB_MAP = {}
        
    def process_corpus(self, csv_data: Union[Path, StringIO], base_namespace: str = 'https://w3id.org/stlab/mr_data/', delimiter: str = None):
        
        gstore = GraphStore()
        
        meta_g = Graph()
        
        #corpus_id;id;﻿sentence_id;content
        
        #id = shortuuid.uuid()[:8]
        
        df: pd.DataFrame = pd.read_csv(csv_data, sep=delimiter)
        
        
        meta_ns = Namespace(base_namespace + 'meta/')
        corpus_ns = Namespace(meta_ns + 'Corpus/')
        document_ns = Namespace(meta_ns + 'Document/')
        sentence_ns = Namespace(meta_ns + 'Sentence/')
        content_ns = Namespace(meta_ns + 'Content/')
            
        #reader = csv.reader(csv_data, delimiter=delimiter)
        #is_header = True
        for index, row in df.iterrows():
            
            corpus_id = str(row['corpus_id'])
            document_id = str(row['document_id'])
            sentence_id = str(row['sentence_id'])
            
            corpus = corpus_ns[str(corpus_id)]
            document = document_ns[f'{corpus_id}_{document_id}']
            sentence = sentence_ns[f'{corpus_id}_{document_id}_{sentence_id}']
            
            content = row['content']
            
            #content_id = shortuuid.uuid(content)[:8]
            
            
            meta_g.add((corpus, RDF.type, MRO.Corpus))
            meta_g.add((corpus, RDFS.label, Literal(f'Corpus {corpus_id}')))
            
            meta_g.add((document, RDF.type, MRO.Document))
            meta_g.add((sentence, RDF.type, MRO.Sentence))
            
            meta_g.add((corpus, MRO.hasPart, document))
            meta_g.add((document, RDFS.label, Literal(f'Document {document_id} part of corpus {corpus_id}')))
            
            meta_g.add((document, MRO.hasPart, sentence))
            meta_g.add((sentence, MRO.hasContent, Literal(content)))
            meta_g.add((sentence, RDFS.label, Literal(f'Sentence {sentence_id} part of document {document_id} part of corpus {corpus_id}')))
            
            
            corpus_doc_sent_id = f'{corpus_id}_{document_id}_{sentence_id}'
            
            machine_reader_ns = Namespace(meta_ns + 'MachineReader/')
            machine_reading_ns = Namespace(meta_ns + 'MachineReading/')
            
        
            for machine_reader in self._maschine_readers:
                reader_name = machine_reader.get_name()
                local_namespace = f'{base_namespace}{corpus_doc_sent_id}_{reader_name}'
                
                graph_id = f'{base_namespace}/Graph/{corpus_doc_sent_id}_{reader_name}'
                
                machine_reader_uriref = machine_reader_ns[reader_name]
                machine_reading = machine_reading_ns[corpus_doc_sent_id]
                
                meta_g.add((machine_reader_uriref, RDF.type, MRO.MachineReader))
                meta_g.add((machine_reading, RDF.type, MRO.MachineReading))
                meta_g.add((machine_reading, RDFS.label, Literal(f'Machine reading process set with the reader {reader_name} for the sentence {sentence_id} part of document {document_id} part of corpus {corpus_id}')))
                
                meta_g.add((machine_reading, MRO.hasInput, sentence))
                meta_g.add((machine_reading, MRO.hasOutput, URIRef(graph_id)))
                meta_g.add((machine_reading, MRO.usesReader, machine_reader_uriref))
                
                meta_g.add((URIRef(graph_id), RDF.type, MRO.Graph))
                meta_g.add((URIRef(graph_id), RDFS.label, Literal(f'Graph produced by {reader_name} for the sentence {sentence_id} part of document {document_id} part of corpus {corpus_id}')))
                
                print(f'Processing row {index} with content: {content}')
            
                g = machine_reader.read(content, namespace=f'{local_namespace}/')
                
                if g:
                    gstore.add_named_graph(g, URIRef(local_namespace))
                
            
            gstore.add_named_graph(meta_g, meta_ns)
            
            
        
        
        return gstore
        
        '''
        csv_data = StringIO(request.data.decode())
        
        global action
        def action():
        
            gstore = GraphStore()
            
            reader = csv.reader(csv_data, delimiter=',')
            for row in reader:
                text = row[0]
                print(f'Processing: {text}')
                self._workflow.process_text(text, base_namespace, gstore)
            
            return gstore
        
        t = Thread(target=action)
        t.start()
        
        id = uuid.uuid4().hex
        
        CorpusProcessor.__JOB_MAP[id] = t
        
        out = {
            'job_id': id,
            'job_url': f'{request.url_root}/{id}' 
            }
        
        return json.dumps(out, indent=4)
        '''
        
        

@ComponentFactory("job-manager-factory")
@Provides("job-manager")
@Instantiate("job-manager-impl")
class JobManager(object):
    
    __JOB_MAP = None
    
    @Validate
    def validate(self, context):
        JobManager.__JOB_MAP = {}
    
    def execute_job(self, target: callable, callback: callable, target_args: Dict[str, object] = {}, callback_args: Dict[str, object] = {}) -> object:
        job_id = uuid.uuid4().hex
        
        job = Job(job_id, target, callback, target_args, callback_args)
        
        JobManager.__JOB_MAP[job_id] = job
        
        job.start()
        
        #t = Thread(target=target, args=args, kwargs=kwargs)
        #t.start()
        
            
        
        return job_id
    
    def get_job(self, job_id: str) -> Thread:
        
        if job_id in JobManager.__JOB_MAP:
            
            return JobManager.__JOB_MAP[job_id]
        
        raise JobNotFoundException(job_id)
    
class Job(Thread):
    def __init__(self, id: str, target: callable, callback: callable, target_args: Dict[str,object] = {}, callback_args: Dict[str,object] = {}):
        super().__init__()
        self.__id = id,
        self.__target = target
        self.__callback = callback
        self.__target_args = target_args
        self.__callback_args = callback_args
    
    def run(self):
        out = self.__target(**self.__target_args)
        return self.__callback(out, self.__id, **self.__callback_args)
    


class JobNotFoundException(Exception):
    def __init__(self, job_id: str, message: str ="The job with ID {0} cannot be found in the registry."):
        self.__job_id= job_id
        self.message = message.format(job_id)
        super().__init__(self.message)
        
    def get_job_id(self):
        return self.__job_id