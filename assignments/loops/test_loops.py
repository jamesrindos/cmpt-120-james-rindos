from math import pi

from myloops import *


class TestClass:
    '''
    This class contains the test functions for lab assignment 3.
    '''

    def test_get_nums(self):
        '''
        Test that executes a function print_nums(n) that doesn't return
        a defined an explicit value. 
        '''
        assert calculate_sum(1) == 0
        assert calculate_sum(3) == 3
        assert calculate_sum(5) == 10

    def test_calculate_pi(self):
        '''
        Test that executes the function calculate_pi(n) the uses the
        Liebniz formula for calculating pi using a series.
        '''
        assert calculate_pi(1000000) == 3.1415916535897743

    def test_fibonacci(self):
        '''
        Test that executes the fibonacci function that uses the 
        fibonacci number sequence to calculate the n number in the
        series.
        '''

        assert fibonacci(1) == 0
        assert fibonacci(2) == 1
        assert fibonacci(3) == 1
        assert fibonacci(4) == 2
        assert fibonacci(12) == 89