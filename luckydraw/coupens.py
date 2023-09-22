from .models import LuckyDraw
import re


# coupen validation check agains its type
class CoupenValidator:
    """
    this class contains methods for coupen validation against its type
    """

    def __init__(self, coupen_number=None, coupen_type=None):
        self.coupen_number = coupen_number
        self.coupen_type = coupen_type

    def is_valied(self):
        """
        calling different validtin fuction accorting to the coupen type
        """
        # if contain specia charecter return false
        if self.is_contain_special_char():
            return False

        if self.coupen_type == "BOX":
            return self.is_box_coupen()
        
        elif self.coupen_type == "BLOCK" or self.coupen_type == "SUPER":
            return self.is_block_or_super()


    def is_box_coupen(self):
        """
        this methods returns True if the coupen is a valied box coupen else return False
        """
        
        # seperate integer to one string, alphabet to another string for checking
        number = ""
        char = ""
        for i in self.coupen_number:
            if i.isnumeric():
                number = number+i
            else:
                char = char+i

        
        if len(number) == 2 and len(char) == 3:
            return False

        # bothe number and char leng must be below 3 and not be zero
        if 0 < len(number) <= 3 or 0 < len(char) <= 3:
            return True

        else:
            return False
            

    def is_block_or_super(self):
        """
        for both block and supen we have a single chicking
        check: three digit number or not
        """

        if self.coupen_number.isnumeric() and len(self.coupen_number) == 3:
            return True
        else:
            return False
        
    
    def is_contain_special_char(self):
        """
        checking the coupen contain any special charecter or not
        if contains returns true 
        """

        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

        if regex.search(self.coupen_number) is not None:
            return True
        else:
            return False
