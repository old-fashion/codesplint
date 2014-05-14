#!/usr/bin/env python

# SKP Code Splint Round 1

import sys
import re
from pprint import *

VERSION="0.1"

def make_model(filename):
  model = {}
  count = 0

  with open(filename) as infile:
    for line in infile:
      for word in re.split("[^a-zA-Z]*", line):
        node = model
        for char in word.lower():
          if char in node:
            node = node[char]
          else:
            node[char] = {}
            node = node[char]
        node['+'] = {}
        count += 1

  del model['+']  
  print "Total count = {}".format(count)
  return model

def query(model, str):
  node = model
  str = str.lower()
  word = ''
  candidate = ''
  result = ''
  index = 0
  cindex = 0

  while index < len(str):
    char = str[index]
    if '+' in node:
      candidate = word 
      cindex = index
 
    if char in node:
      word += char
      node = node[char]
      index += 1
    else:
      if candidate != '':
        result += candidate + ' '
        word = ''
        candidate = ''
        node = model
        index = cindex
      else:
        result += char + ' '
        index += 1
    
  result += word
  
  return result.strip()

def word_tree(model, str):
  tree = {'': str}
  _word_tree(model, tree)
  return tree['']

def _word_tree(model, tree):
  for key, value in tree.iteritems():
    node = model
    prefix = ''

    if value == '':
      continue

    for char in value:
      prefix += char
      if char in node:
        node = node[char] 
      else:
        node = {}
      if '+' in node:
        if type(tree[key]) == type(''):
          tree[key] = {prefix : value[len(prefix):]}
        else:
          tree[key][prefix] = value[len(prefix):]
    _word_tree(model, tree[key])
    
def query_check(model, str):
  a = str.strip().split('\t')
  b = query(model, a[0])
  if b == a[1]:
    print "{} : {} : {} --> PASS".format(a[0], a[1], b)
    return True
  else:
    print "{} : {} : {} --> FAIL".format(a[0], a[1], b)
    return False

def query_check_file(model, filename):
  pc = 0
  fc = 0

  with open(filename) as infile:
    for line in infile:
      result = query_check(model, line) 
      if result:
        pc += 1
      else:
        fc += 1
  
  print "PASS: {}, FAIL: {}, RATE: {}%".format(pc, fc, pc * 100.0 / (pc+fc))

def prefix(model, str):
  node = model
  checked = ''
  for char in str:
    if char in node:
      checked += char
      node = node[char]
    else:
      break
  print "PREFIX = {}".format(checked)
  pprint(node)
      

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(version=VERSION)
  parser.add_argument('--data', required=True, help='Training Data')
  parser.add_argument('--query', help='Query Data')
  parser.add_argument('--prefix', help='Check mode with prefix')
  parser.add_argument('--tree', help='Show possible word tree')
  args = parser.parse_args()

  model = make_model(args.data)
  if args.tree:
    tree = word_tree(model, args.tree)
    pprint(tree)
    sys.exit(0)
  if args.prefix:
    prefix(model, args.prefix)
    sys.exit(0)
  if args.query:
    query_check_file(model, args.query)
  else:
    pprint(model)
 
