import unittest
from bigsky.cfg import Cfg, Nonterminal
from bigsky.cky import enumerate_cky_trees, cky_alg, cky_tree, debinarize, make_trees
from bigsky.cky2json import jsonify_tree, extract_from_sentence
from bigsky.json2cky import treeify_weather, stringify_tree

class TestCky(unittest.TestCase):
    
    
    def setUp(self):
        self.ss = ["humid in the morning.",
                   "windy and mostly cloudy tonight.",
                   "heavy drizzle (4 – 6 in.) throughout the day.",
                   "windy and windy and windy tonight.",
                   "windy and possible light flurries (with a chance of 10 – 3 cm. of snow) starting tomorrow, continuing until tonight and this morning.",
                   "humid until tonight.",
                   "possible heavy snow starting later this morning, continuing until tonight."]  
        self.data = [
            {'type': 'cloud', 'degree': 'heavy', 'probability': 'high', 'measure': 'N/A', 'snow_chance': False},
            {'type': 'cloud', 'degree': 'light', 'probability': 'high', 'measure': 'N/A', 'snow_chance': False},
            {'type': 'humid', 'degree': 'moderate', 'probability': 'high', 'measure': 'N/A', 'snow_chance': False},
            {'type': 'rain', 'degree': 'light', 'probability': 'medium', 'measure': 'UNKNOWN', 'snow_chance': False},
            {'type': 'rain', 'degree': 'heavy', 'probability': 'high', 'measure': {'max': 10, 'unit': 'in.', 'min': 6}, 'snow_chance': True},
            {'type': 'snow', 'degree': 'heavy', 'probability': 'high', 'measure': {'max': 2, 'unit': 'in.', 'min': 0}, 'snow_chance': False}
        ]      
        self.OG = Cfg.from_file("data/cfgs/weather.cfg")            # Original Grammar = OG
        self.g = self.OG.binarize()
    
    def test_enum_cky_tree1(self):
        result = enumerate_cky_trees(self.ss[0], self.g)
        assert result == [[('S', ('WEATHER', 'humid'), 
                            [('__TIME___"."', 
                              [('TIME', ('_"in"', 'in'), 
                                [('___"the"__TIMEWORD', 
                                  ('_"the"', 'the'), 
                                  ('TIMEWORD', 'morning'))])], 
                              ('_"."', '.'))])]]
   
    def test_enum_cky_tree2(self):
        result = enumerate_cky_trees(self.ss[3], self.g)
        result = sorted(result, key = lambda x: str(x))
        assert result == [[('S', [('WEATHER', ('WEATHER', 'windy'), [('___"and"__WEATHER', ('_"and"', 'and'), [('WEATHER', ('WEATHER', 'windy'), [('___"and"__WEATHER', ('_"and"', 'and'), ('WEATHER', 'windy'))])])])], [('__TIME___"."', ('TIME', 'tonight'), ('_"."', '.'))])], [('S', [('WEATHER', [('WEATHER', ('WEATHER', 'windy'), [('___"and"__WEATHER', ('_"and"', 'and'), ('WEATHER', 'windy'))])], [('___"and"__WEATHER', ('_"and"', 'and'), ('WEATHER', 'windy'))])], [('__TIME___"."', ('TIME', 'tonight'), ('_"."', '.'))])]]
       
    def test_cky_tree1(self):
        result = cky_tree(self.ss[2], self.g)
        assert result == [('S', [('WEATHER', ('PRECIPMODIFIERS', 'heavy'), 
                                    [('__PRECIPNOUN__PRECIPPAREN', ('PRECIPNOUN', 'drizzle'), 
                                        [('PRECIPPAREN', ('_"("', '('), 
                                            [('__MEASURE___")"', [('MEASURE', ('NUM', '4'), 
                                                [('___"–"__NUM__UNIT', ('_"–"', '–'), [('__NUM__UNIT', ('NUM', '6'), [('UNIT', ('_"in"', 'in'), ('_"."', '.'))]), 
                                                ('__NUM__UNIT', ('NUM', '6'), [('UNIT', ('_"in"', 'in'), ('_"."', '.'))])])])], ('_")"', ')'))])])])], 
                            [('__TIME___"."', [('TIME', ('_"throughout"', 'throughout'), [('___"the"___"day"', ('_"the"', 'the'), ('_"day"', 'day'))])], ('_"."', '.'))])]    

    def test_cky_tree2(self):
        result = cky_tree(self.ss[0], self.g)
        assert result == [('S', ('WEATHER', 'humid'), 
                            [('__TIME___"."', [('TIME', ('_"in"', 'in'), [('___"the"__TIMEWORD', ('_"the"', 'the'), ('TIMEWORD', 'morning'))])], ('_"."', '.'))])]  

    def test_cky_tree3(self):
        '''make sure the ambiguity appears in the right place'''
        result = cky_tree(self.ss[3], self.g)
        assert len(result[0][1]) == 2 
        
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

    def test_debin1(self):
        tree = enumerate_cky_trees(self.ss[6], self.g)[0]
        result = debinarize(tree, self.OG)
        assert result == ['S',
                            ['WEATHER',
                                ['PRECIP',
                                    ['PRECIPMODIFIERS',
                                        ['PRECIPMODIFIER', 'possible'],
                                        ['PRECIPMODIFIERS', ['PRECIPMODIFIER', 'heavy']]],
                                    ['PRECIPNOUN', 'snow']]],
                            ['TIME',
                                'starting',
                                ['BTIME', 'later', 'this', 'morning'],
                                ',',
                                'continuing',
                                'until',
                                ['BTIME', 'tonight']],
                            '.']

    def test_debin2(self):
        tree = enumerate_cky_trees(self.ss[1], self.g)[0]
        result = debinarize(tree, self.OG)
        assert result == ['S',
                            ['WEATHER', 
                                ['WEATHER', 'windy'], 'and', ['WEATHER', 'mostly', 'cloudy']],
                            ['TIME', ['BTIME', 'tonight']],
                        '.']
    
    def test_jsonify1(self):
        data = extract_from_sentence(self.ss[1], self.OG, self.g)
        assert sorted(data, key=(lambda x: str(x))) == [[{'type': 'wind', 'degree': 'light', 'probability': 'high', 'measure': 'N/A', 'snow_chance': False}, 
                                                        {'type': 'cloud', 'degree': 'moderate', 'probability': 'high', 'measure': 'N/A', 'snow_chance': False}]]

    def test_jsonify2(self):
        data = extract_from_sentence(self.ss[4], self.OG, self.g)
        assert sorted(data, key=(lambda x: str(x))) == [[{'type': 'wind', 'degree': 'light', 'probability': 'high', 'measure': 'N/A', 'snow_chance': False}, 
                                                        {'type': 'snow', 'degree': 'light', 'probability': 'medium', 'measure': {'unit': 'cm.', 'min': 10, 'max': 3}, 'snow_chance': True}], 
                                                       [{'type': 'wind', 'degree': 'light', 'probability': 'high', 'measure': 'N/A', 'snow_chance': False}, 
                                                        {'type': 'snow', 'degree': 'light', 'probability': 'medium', 'measure': {'unit': 'cm.', 'min': 10, 'max': 3}, 'snow_chance': True}]]
    
    def test_treeify1(self):
        result = stringify_tree(treeify_weather(self.data[4]))
        assert result == "heavy rain (with a chance of 6 – 10 in. of snow) "
    
    def test_treeify2(self):
        assert stringify_tree(treeify_weather(self.data[3])) == "possible drizzle "

    def test_treeify3(self):
        assert stringify_tree(treeify_weather(self.data[0])) == "overcast "

if __name__ == "__main__":
	unittest.main()
