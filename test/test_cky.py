import unittest
from bigsky.cfg import Cfg, Nonterminal
from bigsky.cky import enumerate_cky_trees, cky_alg

class TestCky(unittest.TestCase):
    
    
    def setUp(self):
        self.ss = ["humid in the morning.",
                   "windy and mostly cloudy tonight.",
                   "heavy drizzle (4 – 6 in.) throughout the day.",
                   "windy and windy and windy tonight.",
                   "windy and possible light flurries (with a chance of 10 – 3 cm. of snow) starting tomorrow, continuing until tonight and this morning.",
                   "humid until tonight.",
                   "possible heavy snow starting later this morning, continuing until tonight."]        
        g = Cfg.from_file("data/cfgs/weather.cfg")
        self.g = g.binarize()
    
    def test_cky_tree1(self):
        result = enumerate_cky_trees(self.ss[0], self.g)
        assert result == [[('S', ('WEATHER', 'humid'), 
                            [('__TIME___"."', 
                              [('TIME', ('_"in"', 'in'), 
                                [('___"the"__TIMEWORD', 
                                  ('_"the"', 'the'), 
                                  ('TIMEWORD', 'morning'))])], 
                              ('_"."', '.'))])]]
   
    def test_cky_tree2(self):
        result = enumerate_cky_trees(self.ss[3], self.g)
        result = sorted(result, key = lambda x: str(x))
        assert result == [[('S', [('WEATHER', ('WEATHER', 'windy'), [('___"and"__WEATHER', ('_"and"', 'and'), [('WEATHER', ('WEATHER', 'windy'), [('___"and"__WEATHER', ('_"and"', 'and'), ('WEATHER', 'windy'))])])])], [('__TIME___"."', ('TIME', 'tonight'), ('_"."', '.'))])], [('S', [('WEATHER', [('WEATHER', ('WEATHER', 'windy'), [('___"and"__WEATHER', ('_"and"', 'and'), ('WEATHER', 'windy'))])], [('___"and"__WEATHER', ('_"and"', 'and'), ('WEATHER', 'windy'))])], [('__TIME___"."', ('TIME', 'tonight'), ('_"."', '.'))])]]
       
        
    def test_cky_alg(self):
        words = "humid in the morning".split() + ['.']
        table = cky_alg(words, self.g)
        top_cell = table[0][5]
        assert len(list(top_cell)) == 1
        top_cell_element = list(top_cell)[0]
        assert top_cell_element[0] == Nonterminal('S')
        assert top_cell_element[1] == 1
        
    def test_cky_alg2(self):
        words = "windy and windy and windy tonight".split() + ['.']
        table = cky_alg(words, self.g)
        top_cell = table[0][5]
        assert len(list(top_cell)) == 2
        ambig_element1 = sorted(top_cell)[0]
        ambig_element2 = sorted(top_cell)[1]
        assert ambig_element1[0] == Nonterminal('WEATHER')
        assert ambig_element1[1] == 1
        assert ambig_element2[0] == Nonterminal('WEATHER')
        assert ambig_element2[1] == 3
        
        
if __name__ == "__main__":
	unittest.main()
