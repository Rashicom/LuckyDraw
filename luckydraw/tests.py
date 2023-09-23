from django.test import TestCase
from .coupens import CoupenValidator

# Create your tests here.

# coupen validator checking

class CoupenValidatorTest(TestCase):

    # valied coupens
    block_valied_coupens = ["123","111","121","122"]
    super_valied_coupens = ["123","111","121","122"]
    box_valied_coupens = ["ABC1","abc1","aBc1","A1","AB1","AB23","aB24","CA1"]

    # invalied coupens
    block_invalied_coupens = ["12","1115","","5","AB1","a"]
    super_invalied_coupens = ["12","1115","","5","AB1","a"]
    box_invalied_coupens = ["ABC","abc","121","A12","AB123","ABCD","AD1","","AB_1","ABA1","AB3455"]

    # valied coupen checking
    def test_block_valied_coupen(self):

        for coupen in self.block_valied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="BLOCK")
            self.assertTrue(validator.is_valied(), f"Validation failed for coupen: {coupen}")


    def test_super_valied_coupen(self):
        
        for coupen in self.super_valied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="BLOCK")
            self.assertTrue(validator.is_valied(), f"Validation failed for coupen: {coupen}")
    


    def test_box_valied_coupens(self):

        for coupen in self.box_valied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="BOX")
            self.assertTrue(validator.is_valied(), f"Validation failed for coupen: {coupen}")

    
    
    # invalied coupen checking
    def test_block_invalid_coupens(self):

        for coupen in self.block_invalied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="BLOCK")
            self.assertFalse(validator.is_valied(), f"Validation failed for coupen: {coupen}")

    
    def test_super_invalid_coupens(self):

        for coupen in self.super_invalied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="SUPER")
            self.assertFalse(validator.is_valied(), f"Validation failed for coupen: {coupen}")
    

    def test_box_invalid_coupens(self):

        for coupen in self.box_invalied_coupens:
            validator = CoupenValidator(coupen_number=coupen, coupen_type="BOX")
            self.assertFalse(validator.is_valied(), f"Validation failed for coupen: {coupen}")
    