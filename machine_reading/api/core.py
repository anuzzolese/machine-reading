from abc import ABC, abstractmethod
from rdflib import Graph, URIRef, Dataset
from builtins import object
from rdflib.term import Node
from typing import List

class MachineReader(ABC):
    
    @abstractmethod
    def read(self, text: str, **kwargs) -> Graph:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass


class GraphStore(object):

    def __init__(self):
        self.__dataset = Dataset()
        
    def get_dataset(self) -> Dataset:
        return self.__dataset
    
    def add_named_graph(self, graph: Graph, graphIdentifier: URIRef) -> None:
        namedGraph = self.__dataset.graph(graphIdentifier)
        for s, p, o in graph:
            namedGraph.add((s, p, o))
            
    def get_named_graph(self, graphIdentifier: URIRef) -> None:
        return self.__dataset.get_graph(graphIdentifier)    
            
    def serialize(self, format: str = 'nquads', destination: str = None) -> str:
        nquads = self.__dataset.serialize(destination=destination, format=format)
        return nquads
    
class Metadata(object):
    
    def __init__(self, **kwargs):
        self.__metadata = {**kwargs}
        
    def add(self, key: URIRef, value: Node) -> None:
        self.__metadata.update({key: value})
        
    def get(self, key: URIRef) -> Node:
        return self.__metadata[key] if key in self.__metadata else None
    
    def remove(self, key: URIRef) -> None:
        if key in self.__metadata:
            del(self.__metadata[key])
    
class Text(object):
    
    def __init__(self, content: str, metadata: Metadata = None):
        self.__content = content
        self.__metadata = metadata
        
    def get_content(self) -> str:
        return self.__content
    
    def get_metadata(self) -> Metadata:
        return self.__metadata
        
        
class Corpus(object):
    
    def __init__(self, texts: List[Text] = None):
        self.__texts = texts if texts else []
        
    def add(self, text: Text):
        self.__texts.append(text)