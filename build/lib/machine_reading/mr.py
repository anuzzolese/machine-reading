from pelix.framework import Framework, create_framework
from builtins import classmethod
import os, codecs, sys
from pathlib import Path
from argparse import ArgumentParser
        
        
class MR(object): 
    
    __mrp : 'MRP' = None
    __framework : Framework
        
    @classmethod
    def start(cls):
        if not cls.__mrp:
            
            parser = ArgumentParser()
            parser.add_argument("-o", "--output", dest="output",
                    help="Output file. If no choice is provided then standard output is assumed as default.", metavar="NQuad out file")
            
            parser.add_argument("-d", "--delimiter", dest="delimiter",
                    help="The delimiter used in the CSV for separating columns, e.g. ',', ';', '\t', etc. If no choice is provided then ',' is used as default.", metavar="CSV delimiter")
            
            parser.add_argument("-n", "--namespace", dest="namespace",
                    help="The base namespace used for generating URIs. If no choice is provided then 'https://w3id.org/stlab/mr_data/' is used as default.", metavar="Base namespace")
            
            parser.add_argument("-m", "--mode", dest="mode",
                    help="The modality adopted for running the script. Possible values for this argument: (i) fred; (ii) amr2fredbase; (iii) all. In case 'fred' or 'amr2fred' are used then only Fred or AMR2FRED are used for generating graphs, respectively. If 'all' is provided all machine readers are used. If no value is provided for this argument the 'all' is used as default.", metavar="Modality")
            
            parser.add_argument("input", help="The input RML mapping file for enabling RDF conversion.")
        
            args = parser.parse_args()
            
            
            
            if not args.mode:
                modality = 'all'
            else:
                modality = args.mode
                
            if not args.namespace:
                namespace = 'https://w3id.org/stlab/mr_data/'
            else:
                namespace = args.prefix
                
            if not args.delimiter:
                delimiter = ','
            else:
                delimiter = args.delimiter
            
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
            
            if modality == 'all':
                for f in os.listdir('./readers'):
                    if f.endswith('.py'):
                        f = f[:-3]
                        mcr_bundles.append(cls.__framework.install_bundle(f, './readers'))
            elif modality == 'fred':
                mcr_bundles.append(cls.__framework.install_bundle('fred', './readers'))
            elif modality == 'amr2fred':
                mcr_bundles.append(cls.__framework.install_bundle('amr', './readers'))
                    
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
            
            ctx = cls.__framework.get_bundle_context()
            service_ref = ctx.get_service_reference('corpus-processor')
            corpus_processor = ctx.get_service(service_ref)
            gstore = corpus_processor.process_corpus(data, namespace, delimiter)
            
            
            
            if args.output:
                dest_folder = Path(args.output).parent
            
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                    
                gstore.serialize(destination=args.output)
                
                #with codecs.open(args.output, 'w', encoding='utf8') as out_file:
                #    out_file.write(gstore.serialize(format='nquads'))
            else:
                print(gstore.serialize())
                
            cls.__framework.stop()
            
        
        else:
            return None
            
        
            
        
        
if __name__ == '__main__':
    sys.exit(MR.start() or 0)
    