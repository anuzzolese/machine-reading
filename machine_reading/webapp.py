from pelix.ipopo.decorators import ComponentFactory, Requires, Instantiate, Validate
from flask import Flask, Response, render_template, request
import shortuuid
from rdflib.graph import Graph
from io import StringIO
import csv
from api.api import GraphStore 

@ComponentFactory("webapp-consumer-factory")
@Requires('_mcr', "machine-reading-workflow")
@Requires('_corpus_processor', "corpus-processor")
@Instantiate("webapp")
class WebApp(object):
    
    myapp = None
        
    def __init__(self):
        self._mcr= None
        
    @Validate
    def validate(self, context):
        print("Web app is starting")
        WebApp.myapp = Flask(__name__)
        WebApp.myapp.add_url_rule('/', 'index', self.index)
        WebApp.myapp.add_url_rule('/csv', 'csv', self.csv, methods=['POST'])
        WebApp.myapp.run(port=5555)
        print("Web app running")
        

    def index(self):
        #return render_template("index.html", basepath='./')
        g = self._mcr.process_text('Miles Davis was an american jazz musician.')
        print(g.serialize(format='nquads'))
        return g.serialize(format='nquads')
    
    
    def csv(self):
        
        gstore = GraphStore()
        
        data = request.data
        f = StringIO(data.decode())
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            text = row[0]
            print(f'Processing: {text}')
            self._mcr.process_text(text, gstore=gstore)
        
        return gstore.serialize(format='nquads')

