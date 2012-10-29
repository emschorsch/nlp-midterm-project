#! /usr/bin/python
from trie import Trie #for the trie class code
from counts import partition,get_peaks
from stats import *
import re

"""
Implement a couple of algorithms from the paper by Hafer and Weiss
"""
TRIE=Trie() #instantiate the trie
RTRIE=Trie(reverse=True) #instantiate trie for predecessor counts
WORDS={} #segmentation data
TESTFILE='/data/cs65/morphology/segments.eng'
#TESTFILE='newWords.txt'

def numCorrect(word, seg, totCorrect,totBounds):
  corWord = WORDS[word]
  j = 0
  length = max(len(seg),len(corWord))
  for i in range(length):
    if j>= length-2:
      break
    if corWord[i] == ' ':
      totBounds += 1
      if seg[j] == ' ':
        totCorrect+=1
        j += 1
    elif seg[j] == ' ':
      j+=2
      if j >= length -1:
        break
    else:
      j+=1
    if j >= length - 1:
      break
  return totCorrect, totBounds

def cutoff_accuracy(segments, cut = 5, rcut = 17, rev=False, duo=False, \
    sumCut = False, duoPeaks = False, sumPeaks = False, negFreq = False, \
    hybrid = False):
  """
  grades the segments
  """
  totCorr = 0
  totCuts = 0
  totBounds = 0
  for word in WORDS:
    if re.search(r'-',word):
      words = word.split('-')
      seg = words[0]
      for i in range(1,len(words)):
        seg1, totCuts = cutoff_segment(words[i], cut, rcut, totCuts, rev,duo, \
          sumCut, duoPeaks, sumPeaks, negFreq, hybrid)
        if seg1[0]== ' ':
          seg = seg + " - " + seg1[1:]
        elif seg1[len(seg1)-1]==' ':
          seg = seg + " - " + seg1[:len(seg1)-2]
        else:
          seg = seg + " - " + seg1
        totCuts+=2
    else:
      seg, totCuts = cutoff_segment(word, cut, rcut, totCuts, rev,duo,sumCut, \
        duoPeaks, sumPeaks, negFreq, hybrid)
    totCorr, totBounds = numCorrect(word, seg, totCorr,totBounds)
    #print word, seg, WORDS[word]

  precision, recall, f = compute_stats(totCuts, totCorr, totBounds)
  precisionStr = "precision: " + str(precision)
  recallStr = "\trecall: " + str(recall)
  return precisionStr + recallStr + "\tf: " + str(f)

def cutoff_segment(word, cutoff, rcut, totCuts, reverse, duo, \
    sumCut, duoPeaks, sumPeaks, negFreq, hybrid):
  """
  segments words base on cutoff frequency
  """
  counts = []
  if reverse:
    counts = RTRIE.predecessorCount(word)
  else:
    counts = TRIE.successorCount(word)
  
  if duo:
    rcounts = RTRIE.predecessorCount(word)
    cutList = get_duoCutoffs(counts, rcounts, cutoff, rcut)
  elif sumCut:
    rcounts = RTRIE.predecessorCount(word)
    cutList = get_sumCutoffs(counts, rcounts, cutoff)
  elif duoPeaks:
    rcounts = RTRIE.predecessorCount(word)
    cutList = get_duoPeaks(counts, rcounts)
  elif sumPeaks:
    rcounts = RTRIE.predecessorCount(word)
    cutList = get_sumPeaks(counts, rcounts)
  elif negFreq:
    cutList = get_negFreq(word)
  elif hybrid:
    rcounts = RTRIE.predecessorCount(word)
    cutList = get_hybrid(word, counts, rcounts)
  else:
    cutList = get_cutoffs(counts,cutoff,reverse)
  totCuts+= len(cutList)
  parts = partition(word, cutList)
  return ' '.join(parts), totCuts

def get_duoCutoffs(counts, rcounts, cutoff, rcut):
  """
  Given two lists of counts, returns another list identifying
  the points where both counts are above the cutoff
  """
  seg1 = get_cutoffs(counts, cutoff)
  segRev = get_cutoffs(rcounts, rcut, True)
  segRev = [segRev[i]-1 for i in range(len(segRev))]
  segList = list(set(seg1) & set(segRev))
  segList.sort()
  return segList

def get_sumCutoffs(counts, rcounts, cutoff):
  """Given two lists of counts, returns another list
  identifying the points where the sum of the counts are above the cutoff
  """
  thresh = []
  start = 2
  if len(counts) < 2:
    return thresh
  for i in range(start, len(counts)-1):
    if counts[i] + rcounts[i] >= cutoff:
      thresh.append(i)
  return thresh

def get_cutoffs(counts, cutoff, predecessor=False):
  """
  Given a list of counts, returns another list identifying
  the points where the counts are above the cutoff
  """
  thresholds = []
  start = 0
  if len(counts) < 2:
    return thresholds

  if not predecessor:
    start = 1#one char prefixes are tricky

  for i in range(start, len(counts)):
    if counts[i] >= cutoff:
      thresholds.append(i+1)
      """if predecessor:#segmenting of predecessor peaks should be one before
        thresholds.append(i)
      else:
        thresholds.append(i+1)"""

  return thresholds

def get_duoPeaks(counts, rcounts):
  """
  Given two lists of counts, returns another list identifying
  the points where both counts are at a peak or plateau
  """
  seg1 = get_peaks(counts)
  segRev = get_peaks(rcounts, True)
  segList = list(set(seg1) & set(segRev))
  segList.sort()
  return segList

def get_sumPeaks(counts,rcounts):
  """
  Given two lists of counts, returns another list identifying
  the points where the sum of the counts is at a peak or plateau
  """
  return get_peaks([counts[i]+rcounts[i+1] for i in range(len(counts)-1)])

def get_negFreq(word):
  """
  Given a word, returns a list identifying the substrings of length
  4 or more that appear as seperate full words in the corpus
  """
  segList = []
  for i in range(4,len(word)):
    if TRIE.isMember(word[:i]):
      segList.append(i)
  return segList

def get_hybrid(word, counts, rcounts):
  """
  Given a word, returns a list identifying the points where both successor
  and predecessor counts to some differing degree indicate a segment.
  """
  segList = []
  negHits = get_negFreq(word)
  for i in range(len(counts)-1):
    if i in negHits and rcounts[i] > 3:
      segList.append(i)
    elif rcounts[i] > 18 and (counts[i] > 1 or i in negHits):
      segList.append(i)
  return segList

def main():
  #build the list of test words
  f = open(TESTFILE, 'r')
  segments = map(lambda f: f.strip('\n'), f.readlines())
  f.close()
  
  #build dictionary of words vs segments
  for word in segments:
    tmp = word.split('\t')
    WORDS[tmp[0]] = tmp[1] #put the kv pairing
 
  #TRIE.pretty_print()
  print "rev: " + cutoff_accuracy(segments, 14, rev=True)
  print "duo: " + cutoff_accuracy(segments,2,10,duo=True)
  print "sumCut: " + cutoff_accuracy(segments,22,sumCut=True)
  print "duoPeaks: " + cutoff_accuracy(segments, duoPeaks=True)
  print "sumPeaks: " + cutoff_accuracy(segments, sumPeaks=True)
  print "negFreq: " + cutoff_accuracy(segments, negFreq=True)
  print "hybrid: " + cutoff_accuracy(segments, hybrid=True)
  #print RTRIE.predecessorCount("low-keyed") 
  #print TRIE.successorCount("low-keyed")
  #print RTRIE.predecessorCount("banquets")
  #print TRIE.successorCount("banquets")
  
  
if __name__=='__main__':
  main()
