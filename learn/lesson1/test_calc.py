from calc import add, safe_divide

def test_add_two_positive_numbers():
     assert add(2, 3) == 5

def test_safe_divide_normal_case():
     assert safe_divide(10, 2) == 5

def test_safe_divide_by_zero_returns_none():
     assert safe_divide(10,0) is None

 