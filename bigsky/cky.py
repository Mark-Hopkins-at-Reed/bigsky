from bigsky.cfg import Terminal, Nonterminal
from sacremoses import MosesTokenizer
from queue import Queue
import copy
import json

def can_be_nonterminal(nonterminal, nts):
    """returns whether a given nonterminal is in a set of nonterminals"""
    ntl = list(nts)
    for ntt in ntl:
        if ntt[0] == nonterminal:
            return True
    return False

def cky_alg(words, grammar):
    """Based on pseudocode in Jurafsky and Martin."""
    """Put this in its own function for modularity. Now I can use it to extract the tree(s)"""
    chart = [[set() for i in range(len(words) + 1)]                 # n+1 x n+1 matrix of sets
             for j in range(len(words) + 1)]
    for j in range(1, 1 + len(words)):
        rules = grammar.get_rules_with_rhs([Terminal(words[j-1])])  # rules that can make this word
        nts = set([(rule.lhs, -1) for rule in rules])               # set of possible pre-terminals
        chart[j-1][j] = chart[j-1][j] | nts                         # add that set to table
        for i in range(j-2, -1, -1):                                # go upwards from here
            for k in range(i+1, j):                                 # and for all possible split points
                nt_pairs = [(x[0], y[0])                            # make a list of all possible combinations of constituents
                            for x in chart[i][k]                    # given the break point
                            for y in chart[k][j]]
                for nt_pair in nt_pairs:                            # for each combo,
                    rules = grammar.get_rules_with_rhs(nt_pair)     # if there's a pair that produces something
                    nts = set([(rule.lhs, k) for rule in rules])    # set of rules with their break-point
                    chart[i][j] = chart[i][j] | nts                 # add it to the set of things this could be
    return chart

def cky_parse(sent, grammar):
    """
    returns whether a sentence can be parsed with a given CFG
    (this was the original thing in here)
    """
    words =  MosesTokenizer().tokenize(sent)
    chart = cky_alg(words, grammar)
    return can_be_nonterminal(Nonterminal("S"),                      # if I can make a sentence, return it
                            chart[0][len(words)])               

def cky_tree(sent, grammar):
    """Returns the parse tree(s) of a given sentence and CFG"""

    # is this exponential time? nobody likes that :(
    # determine whether it is, and if so, then try a bottom-up (rather than
    # top-down approach)
    def recursive_helper(target, i, j):
        """Builds the tree that turns words i to j into a target nonterminal"""
        if j-i <= 1:                                                            # base case: looking at one word
            return (str(target),words[i])
        nts = list(chart[i][j])
        ans_trees = []
        rules = grammar.get_rules_with_lhs(target)
        for nt in nts:                                                          # for each nonterminal in this node
            if nt[0] == target:                                                 # if it's what I'm looking for
                for r in rules:                                                 # go through all the rules that can make the target
                    if (can_be_nonterminal(r.rhs[0], chart[i][nt[1]]) and       # and if I can make the constituents
                        can_be_nonterminal(r.rhs[1], chart[nt[1]][j])):
                        ans_trees.append((str(target), 
                                        recursive_helper(r.rhs[0], i, nt[1]),   # add the constituent trees to this list
                                        recursive_helper(r.rhs[1], nt[1],j)))   # of possible trees
        return ans_trees

    words =  MosesTokenizer().tokenize(sent)
    chart = cky_alg(words, grammar)
    if not can_be_nonterminal(Nonterminal("S"),                     # first, make sure there _is_ a tree
                            chart[0][len(words)]):              
        return False
    trees = recursive_helper(Nonterminal("S"), 0, len(words))       # treeificate with that function
    return trees
    
def enumerate_cky_trees(sent, grammar):
    trees = cky_tree(sent, grammar)
    
    # and now I have a list of trees whose subtrees may include lists of subtrees
    # it would be nice if those were all separated - ie if there are 2 possible
    # parses of a given phrase, we then create two entire trees. I think this is going 
    # to be a rather intensive process if we have really ambiguous sentences so I 
    # have provided a turn-off flag (split_trees)
    def find_ambiguity(start):
        """Searches for an ambiguity and returns a pointer to it"""
        if len(start) > 1 and type(start) == list:                          # If this list is long, found it
            return start
        if len(start[0]) <= 2:                      # If the next thing is a terminal, cant find
            return False
        return (find_ambiguity(start[0][1]) or      # else, check the left and the right of my one thing
                find_ambiguity(start[0][2]))

    ans_trees = []                          # list of unambiguous trees
    wq = Queue()                      # work queue
    wq.put(trees)                           # put ambiguous tree in it
    while not wq.empty():                   # while there is something in the queue
        t = wq.get()                        # dequeue, t is pointer to head
        x = find_ambiguity(t)               # find an ambiguity if there is one
        if not x:                           # if not, this tree is done
            ans_trees.append(t)
        else:                               # if yes, its TREE SPLITTIN' TIME!!
            n = len(x)                      # how many things am I gonna need to make?
            for i in range(n):              # go through each option
                u = copy.deepcopy(t)           # make a deep copy of t
                y = find_ambiguity(u)       # since find_amb. is deterministic, y should point to the same place as x but in u
                for j in range(n)[::-1]:    # get rid of the other options. I think just splicing would fail bc 
                    if j == i: continue     # pointers so I'm using list method pop
                    y.pop(j)
                wq.put(u)                   # then add this new tree with the removed ambiguity back onto the queue in case still ambig.
    return ans_trees                        # potentially needless worrying about duplicates

def reformat_tree(t):
    """
    Reformats the output of the CKY parser for the following syntax tree viewer:
        
    http://ironcreek.net/syntaxtree/
    
    """
    s = json.dumps(t)
    s = s.replace('","', '###')
    s = s.replace('"', '')
    s = s.replace(',','')
    s = s.replace('[[','[')
    s = s.replace(']]',']')
    s = s.replace('_','')
    s = s.replace('###', ',')
    return s      