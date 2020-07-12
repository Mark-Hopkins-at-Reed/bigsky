import unittest
import pandas as pd
import numpy as np
import torch
from torch import tensor
from bigsky.datamanager import DataManager

def compare_tensors(expected, result, num_digits = 4):
    compare = zip(expected.tolist(), result.tolist())
    for i, (exp, actual) in enumerate(compare):
        if abs(exp - actual) > 10**(-num_digits):
            print("Element {} is incorrect: {} vs {}.".format(i, 
                                                              expected[i], 
                                                              result[i]))
            return False
    return True  


def assert_invalid(f):
    try: 
        f()
        assert False, "Should have thrown ValueError."
    except ValueError:
        pass    
    
    
class TestDataManager(unittest.TestCase):
 
  
    def setUp(self):
        df1 = pd.DataFrame(np.array([[0, 2, -3.2], 
                                     [1, 5, 6.1], 
                                     [0, 8, 9.8]]),
                           columns=['a', 'b', 'c'])
        self.dmgr1 = DataManager(df1, dtypes = {'a': 'categorical'})
        
        
    def test_select_response(self):
        response, domain_size = self.dmgr1.select_response('a')
        assert compare_tensors(response, tensor([0, 1, 0]))
        assert domain_size == 2
        assert_invalid(lambda: self.dmgr1.select_response('b'))
        assert_invalid(lambda: self.dmgr1.select_response('c'))
  
    
    def test_select_single(self):
        expected = tensor([[2.], 
                           [5.], 
                           [8.]])
        assert torch.all(torch.eq(expected, self.dmgr1.select_single('b')))
        expected = tensor([[1., 0.],
                           [0., 1.],
                           [1., 0.]])
        assert torch.all(torch.eq(expected, self.dmgr1.select_single('a')))


    def test_select(self):
        expected = tensor([[1., 0., 2],
                           [0., 1., 5],
                           [1., 0., 8]])
        assert torch.all(torch.eq(expected, self.dmgr1.select(['a', 'b'])))
        
        
if __name__ == "__main__":
	unittest.main()
