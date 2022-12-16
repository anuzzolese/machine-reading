from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate
from rdflib.graph import Graph
from fredclient.fredclient import FREDClient, FREDParameters
from machine_reading.api.api import MachineReader

@ComponentFactory("fred-factory")
@Property("_key", "fred.key", "")
@Property("_name", "fred.name", "fred")
@Provides("machine-reader")
@Instantiate("fred")
class FRED(MachineReader):
    
    def read(self, text: str, **kwargs) -> Graph:
        self.__fc = FREDClient('http://wit.istc.cnr.it/stlab-tools/fred', key=self._key)
        g = self.__fc.execute_request(text, FREDParameters(**kwargs))
        return g
    
    def get_name(self) -> str:
        return self._name
