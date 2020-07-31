import unittest
from bigsky.json2cky import treeify_weather, stringify_tree, stringify_hour
from bigsky.json2cky import treeify_interval, treeify_time


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
        expected = ['TIME', 'until', ['BTIME', 'this', ['TIMEWORD', 'afternoon']],
                     ',', 'starting', 'again', ['BTIME', 'this', ['TIMEWORD', 'afternoon']]]
        assert treeify_time([[6, 13],[15,20]], 6) == expected
        ### I should note, the CFG will not be able to parse this last one because it doesn't like "TIME and TIME"
        expected = ['TIME', ['TIME', ['TIME', ['BTIME', 'later', 'this', 'morning']], 
                                'and', ['TIME', ['BTIME', 'in', 'the', ['TIMEWORD', 'afternoon']]]], 
                            'and', ['TIME', ['BTIME', 'tomorrow']]]  
        assert treeify_time([[8,9],[13,14],[30,33]],6) == expected
        
  
if __name__ == "__main__":
	unittest.main()
