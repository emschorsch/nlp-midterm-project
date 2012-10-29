#! /usr/bin/python
from trie import Trie #for the trie class code
from counts import *
from stats import metrics, compute_stats

"""
Implement a couple of algorithms from the paper by Dejean
Morphemes as necessary Concept for Structures discovery
in Untagged Corpora
"""
dash='-'
STANDARD={} #the gold standard
WORDS={} #segmentation data
MORPHEMES=[] #list of all the segments found
TESTFILE='/data/cs65/morphology/segments.eng'
AFFIXES=[]

#stuff for stats
CUTS=0
CORRECT_CUTS=0
TRUE_BOUNDARIES=0

def get_segments():
  """
  Get all the morphemes as proposed by the successor counts
  algorithm and insert them into a global list of those 
  morphemes
  """
  global MORPHEMES #make the global variable accessible
  for word in WORDS:
    segments = segment_word(word).split()
    length = len(segments)
    if length > 2:
      prefix = segments[0] + '-'
      suffix = '-' + segments[-1]
      MORPHEMES += [prefix, suffix]
      MORPHEMES += segments[1:length-1]
    elif length == 2:
      #get the shorter of the segments
      first, secnd = segments
      if len(first) < len(secnd):
        MORPHEMES += [first+'-', secnd]
      else:
        MORPHEMES += [first, '-'+secnd]
    else:
      MORPHEMES += segments

def prune(threshold):
  """
  Prune the global list of all morphemes using threshold as the
  'cutoff' value
  """
  global AFFIXES
  valid = []
  morphemes = set(MORPHEMES)
  for morph in morphemes:
    count = MORPHEMES.count(morph)
    if count > threshold:
      valid.append(morph)
      #print morph, count
  AFFIXES += valid
  
def discover_new_morphemes(threshold=2):
  """
  After pruning, use the resulting morphemes to discover new
  morphemes and then return an extended list comprising of the 
  original morphemes together with the 'discovered' ones.
  """
  global AFFIXES
  stems = []
  prefix = 0 #is this a prefix or suffix
  for word in WORDS:
    counts = 0
    stem = None
    for affix in AFFIXES:
      #some checking stuff
      pre = 1 if (affix.startswith(dash) and len(affix.strip(dash)) > 0) else 0
      suf = 1 if (affix.endswith(dash) and len(affix.strip(dash))>0) else 0
      
      if word.startswith(affix.strip(dash)) and pre:
        stem = word.split(affix.strip(dash))[1]
        prefix = 1
        break
        
      elif word.endswith(affix.strip(dash)) and suf:
        stem = word.split(affix.strip(dash))[0]
        break

    #retry all the affixes
    if stem is None: #nothing found
      continue 

    for affix in AFFIXES:
      if prefix and (affix + stem) in WORDS:
        counts += 1
      elif (stem + affix) in WORDS:
        counts += 1
   
    if counts > threshold:
      stems.append(word) #this is an interesting 
  
  #ok we now have all the relevant stems we want. Go through all the words and
  #and pull out any affixes that are attached to the said stem
  for stem in stems:
    words = [x for x in WORDS if stem in x] #get all words with this stem
    words = set(words) #optimize and just get unique cases
    
    for word in words:
      tmp = word.split(stem) #get all parts of the word
      AFFIXES += tmp #get everything in the word other than the stem

  #a lot of empty characters and repeats need to be weeded out
  AFFIXES = filter(lambda x: True if x else False, set(AFFIXES))

def trim_affixes(affixes):
  """
  Given a list of affixes, return a list containing only the longest
  matching affixes
  """
  discard = []
  for affix in affixes:
    for entry in affixes:
      if affix.strip(dash) in entry and affix != entry:
        discard.append(affix)
  
  #remove the discarded entries
  return set(affixes) - set(discard)

def set_diff(a,b):
  """
  Just return the set difference, but maintaining the 
  order of the entries.
  """
  end = a.index(b[-1])
  return a[:end]

def splits(word, affixes):
  """
  Get a word and a list of affixes. Break up the word so that
  You have the affixes from the word together with anything 
  else that remains unsegmented.
  """
  prefix = ""
  suffix = ""
  lstem = word
  rstem = word
  strlen = len(word)
  for affix in affixes:
    index = word.find(affix.strip(dash))
    if index == 0 and affix.endswith(dash):
      prefix = affix.strip(dash)
      lstem = word[len(affix)-1:]
    elif index > strlen-5 and affix.startswith(dash):
      suffix = affix.strip(dash)
      rstem = word[:index]
    continue
  
  stem = word
  if prefix and suffix:
    stem = set_diff(lstem, rstem)
  elif prefix:
    stem = lstem
  elif suffix:
    stem = rstem
  
  return [prefix, stem, suffix]

def segment_words():
  """
  Using the final list of affixes, segment the words using a longest
  match approach, where you segment based on the longest occuring morpheme
  in the word.
  """
  global CUTS
  global CORRECT_CUTS
  global TRUE_BOUNDARIES
  #build the chunks
  for word in STANDARD:
    affixes = trim_affixes([x for x in AFFIXES if x.strip(dash) in word])
    segments = splits(word, affixes)    
    a,b,c = metrics(' '.join(segments), STANDARD[word])
    CUTS += b
    CORRECT_CUTS += a
    TRUE_BOUNDARIES += c

def main():
  #build the list of test words
  f = open(TESTFILE, 'r')
  segments = map(lambda f: f.strip('\n'), f.readlines())
  f.close()
  
  #build dictionary of words vs segments
  for word in segments:
    tmp = word.split('\t')
    STANDARD[tmp[0]] = tmp[1] #put the kv pairing
    WORDS[tmp[0]] = 0

  #print WORDS
  get_segments()
  prune(11)
  discover_new_morphemes()
  segment_words()
  print "Statistics for Dejean algorithm segmentation"
  print "********************************************"
  print compute_stats(CUTS, CORRECT_CUTS, TRUE_BOUNDARIES)
  print
  
if __name__=='__main__':
  main()
 
