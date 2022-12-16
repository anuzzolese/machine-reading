from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate
from rdflib.graph import Graph
from machine_reading.api.core import MachineReader
import urllib, json

@ComponentFactory("amr-factory")
@Property("_endpoint", "amr.endpoint", "http://framester.istc.cnr.it/txt-amr-fred/api/txt-amr-fred?%s")
@Property("_name", "amr.name", "amr")
@Provides("machine-reader")
@Instantiate("amr")
class AMR(MachineReader):
    
    def read(self, text: str, **kwargs) -> Graph:
        params = {'text': text, 
                  'amrParser': 'SPRING', 
                  'format': 'N-TRIPLES'}
        
        if kwargs['namespace']:
            params.update({'namespace': kwargs['namespace']})
        
        params = urllib.parse.urlencode(params)
        
        request = urllib.request.Request(self._endpoint % params)
        try:
            response = urllib.request.urlopen(request)
            output = response.read()
            
            js = json.loads(output)
        
        
            graph_string = js['fredGraph']
        
            return Graph().parse(data=graph_string, format='nt')
        except Exception as e:
            print(e)
            return None
        
    
    def get_name(self) -> str:
        return self._name


if __name__ == "__main__":
    amr = AMR()
    amr.read('Miles Davis was an american jazz musician.')
