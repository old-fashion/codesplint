#!/usr/bin/env python

# SKP Code Splint Round 1

import sys
import re
import cPickle as pickle
import gc
from pprint import *
import datetime

VERSION="0.1"
WORD_MAP_DEPTH=6
TIME_CHECK=False

def char_model(filename):
  model = {}
  count = 0

  with open(filename) as infile:
    for line in infile:
      for word in re.split("[^a-zA-Z0-9]*", line.lower()):
        node = model
        for char in word:
          if char in node:
            node = node[char]
          else:
            node[char] = {}
            node = node[char]
        node['+'] = {}
        count += 1

  del model['+']  
  #print "Total count = {}".format(count)
  return model

def word_model(filename):
  model = {}

  with open(filename) as infile:
    for line in infile:
      node = model
      words = re.split("[^a-zA-Z0-9]*", line.lower())
      for index in xrange(0, len(words)):
        l = words[index:index + WORD_MAP_DEPTH]
        _word_model(model, l)

  return model

def _word_model(model, words):
  node = model
  for word in words:
    if word == '':
      continue
    if word in node:
      node = node[word]
    else:
      node[word] = {}
      node = node[word]
    if '+' in node:
      node['+'] += 1
    else:
      node['+'] = 1

def get_word_model_count(model, words):
  node = model
  for word in words:
    if word in node:
      node = node[word]
    else:
      return 0

  if '+' in node:
    return node['+']
  return 0 

def query_by_char(model, str):
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

def query_by_word(cmodel, wmodel, str):
  elapsed_time()
  tree = word_tree(cmodel, wmodel, str)

  elapsed_time()
  value, result = search_max(tree, '+')
  if result == '':
    elapsed_time()
    value, result = search_max(tree, '-')
  elapsed_time()
  return result

def query(cmodel, wmodel, str):
  result = query_by_word(cmodel, wmodel, str)
  if result == '':
    result = query_by_char(cmodel, str)

  return result

def word_tree(cmodel, wmodel, str):
  elapsed_time("tree 1")
  tree = {'': str}
  _word_tree(cmodel, tree)
  tree = tree['']

  elapsed_time("tree 2")
  _word_tree_count(wmodel, tree, '')
  elapsed_time("tree 3")
  _word_tree_count2(wmodel, tree, '', '')
  elapsed_time("tree 4")

  return tree

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
        if len(prefix) != 1 or prefix == 'a' or prefix == 'i':
          t = value[len(prefix):]
          if t == '':
            t = {}
          if type(tree[key]) == type(''):
            tree[key] = {prefix : t}
          else:
            tree[key][prefix] = t
   
    if type(tree[key]) == type(''):
      tree[key] = {prefix : {}}
    _word_tree(model, tree[key])

def _word_tree_count(model, tree, str):
  if tree == {}:
    tree['+'] = get_word_model_count(model, str.strip().split())
    return
  for key, value in tree.iteritems():
    _word_tree_count(model, value, str + ' ' + key)

def  _word_tree_count2(model, tree, str, last):
  if '+' in tree:
    # Method 1
    sum = 0
    if len(last) != 1:
      for word in str.strip().split():
        sum += get_word_model_count(model, [word])
    tree['-'] = sum

    # Method 2
    #tree['-'] = 100 / len(str.strip().split())

    # Method 3
    sum = 0
    if len(last) != 1:
      for word in str.strip().split():
        count = get_word_model_count(model, [word])
        sum += (count ** (len(word) / 30.0) / max((30.0 - len(word)), 1)) * len(word) 
    tree['-'] = sum * (100 / len(str.strip().split()))

    return

  for key, value in tree.iteritems():
    _word_tree_count2(model, value, str + ' ' + key, key)


def search_max(tree, char):
  max, max_str = _search_max(tree, '', char) 
  return max, max_str.strip()

def _search_max(tree, str, char):
  max = 0
  max_str = ''

  for key, value in tree.iteritems():
    if char in value:
      if value[char] > max:
        max = value[char]
        max_str = str + ' ' + key
    else:
      m, s =_search_max(value, str + ' ' + key, char)
      if m > max:
        max = m
        max_str = s

  return max, max_str  

def query_check(cmodel, wmodel, str):

  a = str.strip().split('\t')
 
  elapsed_time2(False) 
  b = query(cmodel, wmodel, a[0])
  print a[0], ", ", len(a[0]), ", ",
  elapsed_time2(True) 
  '''
  if b == a[1]:
    print "{} : {} : {} --> PASS".format(a[0], a[1], b)
    return True
  else:
    print "{} : {} : {} --> FAIL".format(a[0], a[1], b)
    return False
  '''

def query_check_file(cmodel, wmodel, filename):
  pc = 0
  fc = 0

  with open(filename) as infile:
    for line in infile:
      result = query_check(cmodel, wmodel, line) 
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
      
last_time = datetime.datetime.now()

def elapsed_time(str=''):
  if not TIME_CHECK:
    return
  global last_time
  now = datetime.datetime.now()
  print str, " : ", now - last_time
  last_time = now

def elapsed_time2(out):
  global last_time
  now = datetime.datetime.now()
  if out:
    print (now - last_time).microseconds
  last_time = now

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(version=VERSION)
  parser.add_argument('--data', help='Training Data')
  parser.add_argument('--cmodel', help='Character Model Data')
  parser.add_argument('--wmodel', help='Word Model Data')
  parser.add_argument('--query', help='Query Data')
  parser.add_argument('--prefix', help='Check mode with prefix')
  parser.add_argument('--tree', help='Show possible word tree')
  parser.add_argument('--count', help='Show word model count')
  parser.add_argument('--max', help='Search max value in wordtree')
  parser.add_argument('--word', action='store_true', help='Show word analysis')
  args = parser.parse_args()


  gc.disable()
  if args.data:
    cmodel = char_model(args.data)
    wmodel = word_model(args.data)
    pickle.dump(cmodel, open('cmodel.p', 'wb'))
    pickle.dump(wmodel, open('wmodel.p', 'wb'))
  else:
    if args.cmodel:
      cmodel = pickle.load(open(args.cmodel, 'rb'))
    if args.wmodel:
      wmodel = pickle.load(open(args.wmodel, 'rb'))
  gc.enable()

  if args.tree:
    tree = word_tree(cmodel, wmodel, args.tree)
    pprint(tree)
    sys.exit(0)
  if args.prefix:
    prefix(cmodel, args.prefix)
    sys.exit(0)
  if args.count:
    count = get_word_model_count(wmodel, args.count.split())
    print count
    sys.exit(0)
  if args.max:
    tree = word_tree(cmodel, wmodel, args.max)
    count, str = search_max(tree)
    print count, str
    sys.exit(0)
  if args.word:
    for word in wmodel:
      print "{}, {}, {}".format(word, len(word), get_word_model_count(wmodel, [word]))
    sys.exit(0)
  if args.query:
    query_check_file(cmodel, wmodel, args.query)
  else:
    #pprint(cmodel)
    #pprint(wmodel)
    pass

  elapsed_time()
