#!/usr/bin/env python

# SKP Code Splint Round 1

from pprint import *
import re

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
  result = ''
  index = 0

  while True:
    char = str[index]
    print char
    if not char.isalpha():
      return str
    if char in node:
      node = node[char]
      word += char
    else:
      print word
      result += word + ' '
      word = ''
      node = model
      index -= 1
    index += 1
    if index == len(str):
      result += word + ' '
      break
    
  return result.strip()

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

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(version=VERSION)
  parser.add_argument('--data', required=True, help='Training Data')
  parser.add_argument('--query', help='Query Data')
  args = parser.parse_args()

  model = make_model(args.data)
  query_check_file(model, args.query)
 
