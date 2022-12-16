from rdflib import URIRef
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace import Namespace, DefinedNamespace



class MRO(DefinedNamespace):
    __MRO_NS: str = "https://w3id.org/stlab/machine_reading.owl#"
    _NS: Namespace = Namespace(__MRO_NS)
    Corpus: URIRef
    Document: URIRef
    DocumentPart: URIRef
    Sentence: URIRef
    Content: URIRef
    MachineReading: URIRef
    MachineReader: URIRef
    Graph: URIRef
    isPartOf: URIRef
    hasPart: URIRef
    hasContent: URIRef
    isContentOf: URIRef
    hasInput: URIRef
    isInputOf: URIRef
    usesReader: URIRef
    isReaderUsedBy: URIRef
    hasOutput: URIRef
    isOutputOf: URIRef



