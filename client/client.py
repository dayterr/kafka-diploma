import argparse
import json
import logging
import os
import sys

BDE_PATH = '../bde/bde.json'

parser = argparse.ArgumentParser(
    prog='ClientAPIParser',
    description='Reads the file',
    epilog='See you again')

parser.add_argument('-s', '--search')
parser.add_argument('-r', '--recommendation')  
args = parser.parse_args()

print(args)
