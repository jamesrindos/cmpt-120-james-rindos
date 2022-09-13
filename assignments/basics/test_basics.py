from cgi import test
from primitives import *
from arithmetic import *

class TestClass:
    '''
    This class contains the test functions for lab assignment 1.
    '''
    
    def test_get_int(self):
        '''
        Test that the get_int() function returns an actual integer variable.
        '''
        assert type(get_int()).__name__ == 'int'
        
        
    def test_get_float(self):
        '''
        Test that the get_float() function returns an actual float variable.
        '''
        assert type(get_float()).__name__ == 'float'
        
        
    def test_get_string(self):
        '''
        Test that the get_str() function returns an actual string variable.
        '''
        assert type(get_str()).__name__ == 'str'
        
        
    def test_get_boolean(self):
        '''
        Test that the get_bool() function returns an actual boolean variable.
        '''
        assert type(get_bool()).__name__ == 'bool'
        
        
    def test_add(self):
        '''
        Test that the add(a, b) function properly adds a and b.
        '''
        assert add(3, 3) == 6
        
        
    def test_subtract(self):
        '''
        Test that the subtract(a, b) function properly subtracts b from a.
        '''
        assert subtract(3, 3) == 0
        
        
    def test_multiply(self):
        '''
        Test that the multiply(a, b) function properly multiples a by b.
        '''
        assert multiply(3, 3) == 9
        
        
    def test_divide(self):
        '''
        Test that the divide(a, b) function divides a by b.
        '''
        assert divide(3, 3) == 1
        
        
    def test_power(self):
        '''
        Test that the power(a, b) function properly raises a to the power of bb
        '''
        assert power(3, 3) == 27
        
        
    def test_mod(self):
        '''
        Test that the mod(a, b) function properly get the result of a mod b.
        '''
        assert mod(3, 3) == 0
