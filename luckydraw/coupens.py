from .models import LuckyDraw



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
        if self.coupen_type == "BOX":
            return self.is_box_coupen()
        
        elif self.coupen_type == "BLOCK" or self.coupen_type == "SUPER":
            return self.is_block_or_super()


    def is_box_coupen(self):
        """
        this methods returns True if the coupen is a valied box coupen else return False
        """
        pass
    

    def is_block_or_super(self):
        """
        for both block and supen we have a single chicking
        check: three digit number or not
        """

        if self.coupen_number.isnumeric() and len(self.coupen_number) == 3:
            return True
        else:
            return False