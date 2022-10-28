from pelix.constants import BundleActivator
from pelix.framework import BundleContext, FrameworkFactory, Framework, create_framework
from builtins import classmethod
import os, csv, codecs, sys
from pathlib import Path
from argparse import ArgumentParser
from api.api import GraphStore
        
        
class MR(object): 
    
    __mrp : 'MRP' = None
    __framework : Framework
        
    @classmethod
    def start(cls):
        if not cls.__mrp:
            
            parser = ArgumentParser()
            parser.add_argument("-o", "--output", dest="output",
                    help="Output file. If no choice is provided then standard output is assumed as default.", metavar="NQuad out file")
            parser.add_argument("input", help="The input RML mapping file for enabling RDF conversion.")
        
            args = parser.parse_args()
            
            cls.__mrp = MR()
            
            bundles = [
                 "pelix.ipopo.core",
                 "pelix.shell.core",
                 "pelix.shell.ipopo",
                 "pelix.shell.completion.pelix",
                 "pelix.shell.completion.ipopo",
                 #"pelix.shell.console",
            ]
            
            cls.__framework = create_framework(bundles)
            cls.__framework.start()
            
            mcr_bundles = []
            
            for f in os.listdir('./core'):
                if f.endswith('.py'):
                    f = f[:-3]
                    mcr_bundles.append(cls.__framework.install_bundle(f, './core'))
            
            for f in os.listdir('./readers'):
                if f.endswith('.py'):
                    f = f[:-3]
                    mcr_bundles.append(cls.__framework.install_bundle(f, './readers'))
                    
            #mcr_bundles.append(cls.__framework.install_bundle('webapp', '.'))
            
            for bundle in mcr_bundles:
                bundle.start()
                print(f'Started bundle {bundle}')
                
            print('Framework created.')
            #try:
            #    cls.__framework.wait_for_stop()
            #except KeyboardInterrupt:
            #    cls.__framework.stop()
            #    cls.__mrp = None
            
            
            data = args.input
            
            gstore = GraphStore()
            
            with open(data, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
            
                ctx = cls.__framework.get_bundle_context()
                service_ref = ctx.get_service_reference('machine-reading-workflow')
                workflow = ctx.get_service(service_ref)
            
            
                
                for row in reader:
                    text = row[0]
                    print(f'Processing: {text}')
                    workflow.process_text(text, gstore=gstore)
                    
            if args.output:
                dest_folder = Path(args.output).parent
            
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                
                with codecs.open(args.output, 'w', encoding='utf8') as out_file:
                    out_file.write(gstore.serialize(format='nquads'))
            else:
                print(gstore.serialize(format='nquads'))
                
            cls.__framework.stop()
            
        
        else:
            return None
            
        
            
        
        
if __name__ == '__main__':
    sys.exit(MR.start() or 0)
    