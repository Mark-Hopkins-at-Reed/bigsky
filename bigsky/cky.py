from bigsky.cfg import Terminal, Nonterminal
from sacremoses import MosesTokenizer


def cky_parse(sent, grammar):
    """Based on pseudocode in Jurafsky and Martin."""
    words =  MosesTokenizer().tokenize(sent)
    chart = [[set() for i in range(len(words) + 1)] 
             for j in range(len(words) + 1)]
    for j in range(1, 1 + len(words)):
        rules = grammar.get_rules_with_rhs([Terminal(words[j-1])])
        nts = set([rule.lhs for rule in rules])
        chart[j-1][j] = chart[j-1][j] | nts
        for i in range(j-2, -1, -1):
            for k in range(i+1, j):
                nt_pairs = [(x, y) 
                            for x in chart[i][k] 
                            for y in chart[k][j]]
                for nt_pair in nt_pairs:
                    rules = grammar.get_rules_with_rhs(nt_pair)
                    nts = set([rule.lhs for rule in rules])
                    chart[i][j] = chart[i][j] | nts
    return Nonterminal("S") in chart[0][len(words)]    
        