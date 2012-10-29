#! /usr/bin/python
import pprint
import nltk

"""
Author: Steve Dini and Emanuel Schorsch
Date  : September 26, 2012
CS65 Lab 4 and 5
"""

TERMINAL_SYMBOL='$' #end of word character
VALUE_KEY = '#' #key in dictionary for token freq
class Trie:
  def __init__(self, reverse=False, words=[]):
    self.root = {} #top level of the trie
    self.size = 0 #size of the trie
    self.reverse = reverse #handle successor and predecessor counts
    self.words = map(lambda f: f.strip('\n'),
                     nltk.corpus.brown.words(categories=['news']))\
                     if len(words) == 0 else words
    self.build() #build the trie

  def build(self):
    """
    Get a list of words and build the trie which has the top-level
    as self.struct
    """
    for word in self.words:
      #word = word.lower() #convert everything to lower case
      if self.reverse:
        self.insert(word[::-1]) #reverse the word
      else:
        self.insert(word)

  def getTrie(self):
    """
    A simple accessor method for getting the trie
    """
    return self.root
  
  def predecessorCount(self, fragment):
    """
    Just a wrapped around successor count. More of syntactic sugar to allow
    semantic correctness when the trie is instantiaed with reverse argument
    set to true
    """
    inverted = self.__count__(fragment[::-1], self.root, []) #reverse the word
    return inverted[::-1] #reverse the list

  def successorCount(self, fragment):
    """
    Gets the number of different letters that appear in the left after the word
    passed in.
    """
    return self.__count__(fragment, self.root, []) 

  def __count__(self, fragment, root, counts):
    """
    Method for retrieving the root of the subtree that the last char in the
    fragment is located
    """
    if len(fragment) == 0:
      return counts

    else:
      key = fragment[0]
      if key in root:
        counts.append(len(root[key]))
        return self.__count__(fragment[1:], root[key], counts)
      else:
        counts.append(0)
        return self.__count__(fragment[1:], root, counts)
  
  def __insert__(self, fragment, root):
    """
    Method for just returning a dictionary that maps to the
    current word fragment. Return None if fragment doesn't exist
    """
    if len(fragment) == 0: #are we done?
      return
    
    else:
      key = fragment[0]
      if key in root:
        self.__insert__(fragment[1:], root[key])
      else:
        root[key] = {} #the new entry to insert
        self.__insert__(fragment[1:], root[key])

  def isMember(self, word):
    """
    Method for checking if a certain word, is in the trie. Delegates
    the actual dirty work to the __lookup__ method.
    """
    word += TERMINAL_SYMBOL
    return self.__lookup__(word, self.root)

  
  def __lookup__(self, fragment, root):
    """
    Checks if the current word is contained in the trie.
    Essentially walk through the trie and doing comparisons at each
    level until you can determine if word is then.
    NB: Only works for full words and not fragments
    """
    key = fragment[0]
    if len(fragment) == 1: 
      if len(root.get(key, 'hack')) == 0: #this is a hack!
        return True 
      else:
        return False

    else:
      if key in root:
        return self.__lookup__(fragment[1:], root[key])
      else:
        return False


  def __retrieve__(self, fragment, root):
    """
    Method for retrieving the root of the subtree that the last char in the
    fragment is located
    """
    key = fragment[0]
    if len(fragment) == 1:
      if key in root:
        return root[key]
      else:
        return {} #the word doesn't exist so empty dict returned

    else:
      if key in root:
        return self.__retrieve__(fragment[1:], root[key])
      else:
        return {}  #the word doesn't exist so return empty dict


  def insert(self, word):
    """
    Method for inserting a new word into the trie. Wrapper around the
    __insert__ method by passing in the top-level root of the trie as 
    the argument
    """
    word += TERMINAL_SYMBOL
    self.__insert__(word, self.root)

  def pretty_print(self):
    """
    Print a nice string representation of the object
    """
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(self.root) #pretty print

#************************************************************************
def main():
  t=Trie(reverse=True,words=['food', 'fool', 'foot', 'family', 'eggs',
                             'good', 'mood', 'beard', 'sad', 'breed'])
  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(t.root) #pretty print

  print t.predecessorCount('ford') 
  #print t.successorCount('tset') 
  #print t.successorCount('test') 
if __name__=='__main__':
  main()
