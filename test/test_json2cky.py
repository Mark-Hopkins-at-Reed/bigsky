import unittest
from bigsky.json2cky import treeify_weather, stringify_tree, stringify_hour
from bigsky.json2cky import treeify_interval


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
        assert treeify_interval((6,10), 3) == expected
        expected = ['TIME', 'until', ['BTIME', 'later', 'this', 'morning']]
        assert treeify_interval((6,10), 6) == expected
        expected = ['TIME', ['BTIME', 'later', 'this', 'morning']]
        assert treeify_interval((6,10), 7) == expected
        expected = ['TIME',
                     'starting',
                     ['BTIME', 'this', ['TIMEWORD', 'morning']],
                     ',',
                     'continuing',
                     'until',
                     ['BTIME', 'tomorrow', ['TIMEWORD', 'night']]]
        assert treeify_interval((6,47), 1) == expected
        
  
if __name__ == "__main__":
	unittest.main()
