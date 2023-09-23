from django.test import TestCase
from .coupens import CoupenValidator

# Create your tests here.

# coupen validator checking

class CoupenValidatorTest(TestCase):

    def test_block_valied_coupen(self):
        valied_coupens = ["123","111","121","122"]

        for coupen in valied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="BLOCK")
            self.assertTrue(validator.is_valied())


    def test_super_valied_coupen(self):
        valied_coupens = ["123","111","121","122"]

        for coupen in valied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="BLOCK")
            self.assertTrue(validator.is_valied())
    

    def test_box_valied_coupens(self):
        valied_coupens = ["ABC1","abc1","aBc1","A1","AB1","AB23","aB24","CA1"]

        for coupen in valied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="BOX")
            self.assertTrue(validator.is_valied())

    
    
