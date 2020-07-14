class Nonterminal:
    def __init__(self, sym):
        self.symbol = sym

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        return other.symbol == self.symbol

    def __str__(self):
        return self.symbol

    def is_terminal(self):
        return False
        
class Terminal:
    def __init__(self, sym):
        self.symbol = sym

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        return other.symbol == self.symbol
        
    def __str__(self):
        if '"' not in self.symbol:
            return '"' + self.symbol + '"'
        else:
            return "'" + self.symbol + "'"
            
    def is_terminal(self):
        return True
    
    
class CfgRule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "{} -> {}".format(self.lhs, ' '.join([str(x) for x in self.rhs]))
                
    def binarize(self):
        """Assuming no unary productions for now."""
        if len(self.rhs) == 1:
            return [self]
        elif (len(self.rhs) == 2 and 
              not self.rhs[0].is_terminal() and 
              not self.rhs[1].is_terminal()):
            return [self]
        else:
            rules = []
            new_rhs = []
            for rhs_element in self.rhs:
                if rhs_element.is_terminal():
                    new_rhs.append(Nonterminal('_' + str(rhs_element)))
                    rules.append(CfgRule(new_rhs[-1], (rhs_element,)))
                else:
                    new_rhs.append(rhs_element)
            if len(new_rhs) == 2:
                return rules + [CfgRule(self.lhs, new_rhs)]
            else:
                second_nt = Nonterminal('__' + '__'.join([str(x) for x in new_rhs[1:]]))
                rules.append(CfgRule(self.lhs, (new_rhs[0], second_nt)))
                unbinarized = CfgRule(second_nt, new_rhs[1:])
                binarized = unbinarized.binarize()
                rules += binarized
                return rules
            
    def is_unary(self):
        return len(self.rhs) == 1 and not self.rhs[0].is_terminal()            
                
            
    
    @staticmethod
    def from_string(s):
        try:
            lhs, rhs = s.split('->')
            lhs = lhs.strip()
            rhs = rhs.strip()
            lhs = Nonterminal(lhs)
            rhs_elements = []
            for element in rhs.split():
                if element.startswith('"'):
                    assert(element.endswith('"'))
                    element = element[1:-1]
                    assert('"' not in element)
                    rhs_elements.append(Terminal(element))
                elif element.startswith("'"):
                    assert(element.endswith("'"))
                    element = element[1:-1]
                    assert("'" not in element)
                    rhs_elements.append(Terminal(element))
                else:
                    rhs_elements.append(Nonterminal(element))
        except Exception:
            raise Exception("Unable to parse: {}".format(s))
        return CfgRule(lhs, rhs_elements)

from collections import defaultdict
    
class Cfg:
    def __init__(self, rules):
        self.rules = rules

    def get_rules_with_lhs(self, lhs):
        """TODO: optimize!"""
        return [rule for rule in self.rules if rule.lhs == lhs]
        
    def get_rules_with_rhs(self, rhs):
        return [rule for rule in self.rules if tuple(rule.rhs) == tuple(rhs)]        


    def binarize(self): # TODO: make unique
        new_rules = []
        unary_rules = []
        for rule in self.rules:
            for new_rule in rule.binarize():
                if new_rule.is_unary():
                    unary_rules.append(new_rule)
                else:
                    new_rules.append(new_rule)
        cfg_with_unary = Cfg(new_rules)
        nt_equiv = defaultdict(set)
        result = dict()
        for rule in unary_rules:
            left_nt = rule.lhs
            right_nt = rule.rhs[0]
            nt_equiv[right_nt.symbol].add(left_nt.symbol)
            result = dict(nt_equiv)
        last_result = dict()
        while result != last_result:
            last_result = result
            next_result = dict()
            for key in result:
                next_result[key] = {r for r in result[key]}
                for value in result[key]:
                    if value in result:
                        for value2 in result[value]:
                            next_result[key].add(value2)                    
            result = next_result
        for key in result:
            rules = cfg_with_unary.get_rules_with_lhs(Nonterminal(key))
            for rule in rules:
                for altlhs in result[key]:
                    new_rule = CfgRule(Nonterminal(altlhs), rule.rhs)
                    new_rules.append(new_rule)
        return Cfg(new_rules)
    
    def __str__(self):
        return '\n'.join([str(rule) for rule in self.rules])
    
    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as reader:
            rules = [CfgRule.from_string(line) for line in reader]
        return Cfg(rules)
                
        
        
        