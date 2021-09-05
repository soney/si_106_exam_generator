import argparse
from examGenerator import generateNotebooks, generateSamples

parser = argparse.ArgumentParser(description='SI 106 Jupyter Notebook Generator')
parser.add_argument('ipynb_path', metavar='notebook', help='The path to the .ipynb file')
parser.add_argument('out', metavar='out_directory', help='The directory to place output in')
parser.add_argument('--sample', dest='sample', action='store_true', help='Whether to generate an exhaustive set of samples')

args = parser.parse_args()
if args.sample:
    generateSamples(args.ipynb_path, args.out)
else:
    generateNotebooks(args.ipynb_path, args.out)