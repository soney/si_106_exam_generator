import argparse
from examGenerator import handleNotebook

parser = argparse.ArgumentParser(description='SI 106 Jupyter Notebook Generator')
parser.add_argument('ipynb_path', metavar='notebook', help='The path to the .ipynb file')
parser.add_argument('out', metavar='out_directory', help='The directory to place output in')

args = parser.parse_args()
handleNotebook(args.ipynb_path, args.out)