import unittest
from bigsky.json2cky import treeify_weather, stringify_tree, stringify_hour
from bigsky.json2cky import treeify_interval, treeify_time, treeify


class TestCky(unittest.TestCase):
     
    def setUp(self):
        pass
    
    def test_stringify_hour(self):
        assert stringify_hour(3) == ['night']
        assert stringify_hour(10) == ['morning']
        assert stringify_hour(16) == ['afternoon']
        assert stringify_hour(20) == ['evening']
        assert stringify_hour(22) == ['evening', 'night']
        assert stringify_hour(23) == ['night']
        assert stringify_hour(34) == ['morning']
        
        
    def test_treeify_interval(self):
        expected = ['TIME', ['BTIME', 'in', 'the', ['TIMEWORD', 'morning']]]
        assert treeify_interval([6,10], 3) == expected
        expected = ['TIME', 'until', ['BTIME', 'later', 'this', 'morning']]
        assert treeify_interval([6,10], 6) == expected
        expected = ['TIME', ['BTIME', 'later', 'this', 'morning']]
        assert treeify_interval([6,10], 7) == expected
        expected = ['TIME',
                     'starting',
                     ['BTIME', 'this', ['TIMEWORD', 'morning']],
                     ',',
                     'continuing',
                     'until',
                     ['BTIME', 'tomorrow', ['TIMEWORD', 'night']]]
        assert treeify_interval([6,47], 1) == expected
    
    def test_treeify_time(self):
        expected = ['TIME', 'until', ['BTIME', 'later', 'this', 'morning']]
        assert treeify_time([[6,10]], 6) == expected
        expected = ['TIME', 'starting', ['BTIME', 'later', 'tonight'], 
                    ',', 'continuing', 'until', ['BTIME', 'this', ['TIMEWORD', 'morning']]]  
        assert treeify_time([[1,3],[3,7],[6,9]] , 0) == expected
        expected = ['TIME', 'until', ['BTIME', 'this', ['TIMEWORD', 'evening']]]
        assert treeify_time([[6, 13],[15,20]], 6) == expected
        ### I should note, the CFG will not be able to parse this last one because it doesn't like "TIME and TIME"
        expected = ['TIME', ['TIME', ['TIME', ['BTIME', 'later', 'this', 'morning']], 
                                'and', ['TIME', ['BTIME', 'in', 'the', ['TIMEWORD', 'afternoon']]]], 
                            'and', ['TIME', ['BTIME', 'tomorrow']]]  
        expected = ['TIME', 
                    ['TIME', ['BTIME', 'later', 'this', 'morning']], 'and', 
                    ['TIME', ['BTIME', 'in', 'the', ['TIMEWORD', 'afternoon']]]]
        assert treeify_time([[8,9],[13,14],[30,33]],6) == expected

    def test_treeify(self):
        data = {
            'now': 6,
            'time': [[6,10]],
            'weather': [{'type': 'rain', 
                   'degree': 'heavy', 
                   'probability': 'high', 
                   'measure': {'max': 10, 'unit': 'in.', 'min': 6}, 
                   'snow_chance': True}]
        }
        expected = ['S',
            ['WEATHER', ['PRECIP', 
                    ['PRECIPMODIFIERS', ['PRECIPMODIFIER', 'heavy']], 
                    ['PRECIPNOUN', 'rain'], 
                    ['PRECIPPARENS', ['CHANCEOFSNOW', '(', 'with', 'a', 'chance', 'of', 
                            ['MEASURE', ['NUM', '6'], '–', ['NUM', '10'], ['UNIT', 'in.']], 
                            'of', 'snow', ')']]]],
            ['TIME', 'until', ['BTIME', 'later', 'this', 'morning']], 
            '.'
        ]
        tree = treeify(data)
        assert tree == expected
        assert stringify_tree(tree) == 'heavy rain (with a chance of 6 – 10 in. of snow) until later this morning.'
        data = {
            'now': 6, 'time': [[6,13],[15,20]],
            'weather': [{'type': 'cloud', 
                   'degree': 'heavy', 
                   'probability': 'high', 
                   'measure': 'N/A',
                   'snow_chance': False}]
        }
        expected = ['S', 
                    ['WEATHER', 'overcast'], 
                    ['TIME', 'until', ['BTIME', 'this', ['TIMEWORD', 'evening']]], '.']

        tree = treeify(data)
        assert tree == expected
        assert stringify_tree(tree) == 'overcast until this evening.'

        
  
if __name__ == "__main__":
	unittest.main()
