"""
Helper file that helps with computing some of the statistics.
Given a sample and the actual solution. Determine metrics 
like number of cuts made, total number of cuts and total
number of true boundaries.
"""
def metrics(guess, actual):
  """
  Get the actual and guess and use them to compute some 
  metrics including, number of cuts, correct cuts and 
  true boundaries.
  Guess and actual have to be space-seperated strings
  """
  guess = guess.split()
  actual = actual.split()
  
  correct = 0
  curr = 0
  for segment in guess:
    if segment == guess[0]:
      continue

    for word in actual:
      if word == actual[0]:
        continue

      if (segment[0] == word[0]) and (actual.index(word) > curr):
        correct += 1
        curr = actual.index(word)

  return correct, len(guess), len(actual) 


def compute_stats(cuts, correct_cuts, true_boundaries):
  """
  Compute precision and recall and return those metrics
  """
  if cuts == 0:
    precision = 0
  else:
    precision = float(correct_cuts)/cuts
  recall = float(correct_cuts)/true_boundaries
  f = precision*recall
  return precision, recall, f


  
