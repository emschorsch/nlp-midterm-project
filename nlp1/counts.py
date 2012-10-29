#! /usr/bin/python
from trie import Trie #for the trie class code
from stats import metrics, compute_stats

"""
Implement a couple of algorithms from the paper by Harris
'From Phoneme to Morpheme'. Of particular interest are the 3 algorithms
1. Successor Counts
2. Predecessor Counts
Which we will attempt to work with here
"""

TRIE=Trie() #instantiate the trie
RTRIE=Trie(reverse=True) #instantiate trie for predecessor counts
WORDS={} #segmentation data
TESTFILE='/data/cs65/morphology/segments.eng'

#stuff for the stats
CUTS=0
CORRECT_CUTS=0
TRUE_BOUNDARIES=0

def successor_segmentor():
  """
  User our global list of test words and segment them basing on the successor
  counts that exist within the trie TRIE that we have globally 
  instantiated.
  """
  global CUTS
  global CORRECT_CUTS
  global TRUE_BOUNDARIES

  #initialize
  CUTS, CORRECT_CUTS, TRUE_BOUNDARIES = (0,0,0)
  correct = 0 #number of correct annotations
  
  for word in WORDS:
    a,b,c = metrics(segment_word(word), WORDS[word])
    CUTS += b
    CORRECT_CUTS += a
    TRUE_BOUNDARIES += c
    #print word, segment_word(word), WORDS[word]


def predecessor_segmentor():
  """
  User our global list of test words and segment them basing on predecessor
  counts that exist within the trie RTRIE that we have globally 
  instantiated.
  """
  global CUTS
  global CORRECT_CUTS
  global TRUE_BOUNDARIES

  #initialize
  CUTS, CORRECT_CUTS, TRUE_BOUNDARIES = (0,0,0)
  correct = 0 #number of correct annotations
  
  for word in WORDS:
    a,b,c = metrics(segment_word(word, reverse=True), WORDS[word])
    CUTS += b
    CORRECT_CUTS += a
    TRUE_BOUNDARIES += c
    #print word, segment_word(word, reverse=True), WORDS[word]


def segment_word(word, reverse=False):
  """
  Given a word, return a segmentation of the word based on successor counts
  for the word. If words has not been seen before return the word unsegmented
  """
  counts = []

  if reverse:
    counts = RTRIE.predecessorCount(word) 
  else:
    counts = TRIE.successorCount(word)
  
  parts = partition(word, get_peaks(counts, reverse)) #segment word on the peaks
  return ' '.join(parts)

def partition(alist, indices):
  """
  Given a list and another list of indices, return the original list
  split up at the said indices.
  """
  return [alist[i:j] for i, j in zip([0]+indices, indices+[None])]

def get_peaks(counts, predecessor=False):
  """
  Given a list of counts, return another list identifying where the peaks in
  the list are
  """
  peaks = []
  start = 0
  if len(counts) < 2:
    return peaks

  #differentiate starting point
  if not predecessor:
    start = 2 #one character prefixes are a bit tricky

  for i in range(start, len(counts)-1):
    if counts[i-1] < counts[i] > counts[i+1]:
      if predecessor:
        peaks.append(i)
      else:
        peaks.append(i+1)
  
  return peaks

def statistics(tp, tn, fp, fn):
  """
  Compute statistics of Accuracy, Recall and F-score based on the values
  of True Positives/Negatives and False Positives/Negatives.
  """
  pass

def main():
  #build the list of test words
  f = open(TESTFILE, 'r')
  segments = map(lambda f: f.strip('\n'), f.readlines())
  f.close()
  
  #build dictionary of words vs segments
  for word in segments:
    tmp = word.split('\t')
    WORDS[tmp[0]] = tmp[1] #put the kv pairing
 
  #RTRIE.pretty_print()
  successor_segmentor()
  print "Successor Stats"
  print "****************"
  print compute_stats(CUTS, CORRECT_CUTS, TRUE_BOUNDARIES)
  print
  predecessor_segmentor()
  print "Predecessor Stats"
  print "****************"
  print compute_stats(CUTS, CORRECT_CUTS, TRUE_BOUNDARIES)
  print
  
  
if __name__=='__main__':
  main()

