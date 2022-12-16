import csv
from io import StringIO
import json
import os
import sys
import uuid

from flask import Flask, Response, render_template, request, abort, send_file
from pelix.ipopo.decorators import ComponentFactory, Requires, Instantiate, Validate, Property
from rdflib.graph import Graph
import shortuuid

from machine_reading.api.api import GraphStore 
from machine_reading.core import workflows
from machine_reading.core.workflows import MachineReadingConsumer


def xxx(mcr):
    print(f'ciao {mcr.get_name()}')

def csv_processing(mcr, data):
    gstore = GraphStore()
    
    f = StringIO(data.decode())
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        text = row[0]
        print(f'Processing: {text}')
        mcr.process_text(text, gstore=gstore)
    
    return gstore.serialize(format='nquads')



@ComponentFactory("webapp-consumer-factory")
@Property("_graph_store", "graph.store", "files")
@Requires('_mcr', "machine-reading-workflow")
@Requires('_corpus_processor', "corpus-processor")
@Requires('_job_manager', "job-manager")
@Instantiate("webapp")
class WebApp(object):
    
    myapp = None
    
    __JOB_MAP = None
        
    def __init__(self):
        self._mcr= None
        WebApp.__JOB_MAP = {}
        
    @Validate
    def validate(self, context):
        sys.modules['workflows'] = workflows
        print("Web app is starting")
        
        if not os.path.exists(self._graph_store):
            os.mkdir(self._graph_store)
        WebApp.myapp = Flask(__name__)
        WebApp.myapp.add_url_rule('/', 'index', self.index)
        WebApp.myapp.add_url_rule('/csv', 'csv', self.csv, methods=['POST'])
        WebApp.myapp.add_url_rule('/job/<job_id>', 'job', self.job, methods=['GET'])
        WebApp.myapp.add_url_rule('/graph/<graph>', 'graph', self.graph, methods=['GET'])
        WebApp.myapp.run(port=5555)
        
        print("Web app running")
        

    def index(self):
        #return render_template("index.html", basepath='./')
        g = self._mcr.process_text('Miles Davis was an american jazz musician.')
        print(g.serialize(format='nquads'))
        return g.serialize(format='nquads')
    
    
    
    def csv(self):
        
        target = self._corpus_processor.process_corpus
        callback = lambda gstore, job_id: gstore.serialize(destination=os.path.join(self._graph_store, f'{job_id[0]}.nq'), format='nquads')
        
        target_args = {'csv_data': StringIO(request.data.decode())}
        
        job_id = self._job_manager.execute_job(
            target,
            callback, 
            target_args=target_args)
        
        out = {
            'job_id': job_id,
            'job_url': f'{request.url_root}job/{job_id}' 
            }
        
        return out
    
    def job(self, job_id):
        #job_id = request.view_args['job_id']
        print(f'The job id is {job_id}')
        try:
            job = self._job_manager.get_job(job_id)
            
            print(f'The job found is {job}')
            ret = {'job_id': job_id}
            
            if job.is_alive():
                ret['status'] = 'running'
            else:
                ret['status'] = 'finished'
                ret['ouput'] = f'{request.url_root}graph/{job_id}.nq'
                
            print('out')
            out = json.dumps(ret)
            print(out)
            return Response(json.dumps(ret), mimetype='application/json')
        except Exception as e:
            print(e)
            abort(404)
            
    def graph(self, graph):
        #job_id = request.view_args['job_id']
        
        if os.path.exists(os.path.join(self._graph_store, graph)):
            return send_file(os.path.join(self._graph_store, graph), mimetype='application/n-quads')
        else:
            abort(404)
    
    def csv_(self):
        gstore = GraphStore()
        
        data = request.data
        
        f = StringIO(data.decode('UTF-8'))
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            text = row[0]
            print(f'Processing: {text}')
            self._mcr.process_text(text, gstore=gstore)
        
        return gstore.serialize(format='nquads')
    
    

if __name__ == '__main__':
    x = MachineReadingConsumer()
    