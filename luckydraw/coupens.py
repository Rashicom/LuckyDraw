from .models import LuckyDraw
import re
from .models import Participants,LuckyDraw,LuckyDrawContext


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

        if self.coupen_type == "BLOCK":
            return self.is_block_coupen()
        
        elif self.coupen_type == "BOX" or self.coupen_type == "SUPER":
            return self.is_box_or_super()


    def is_block_coupen(self):
        """
        this methods returns True if the coupen is a valied box coupen else return False
        """

        # if number contain extra char than a b c
        if self.is_contain_extra_char():
            return False

        # seperate integer to one string, alphabet to another string for checking
        number = ""
        char = ""
        for i in self.coupen_number:
            if i.isnumeric():
                number = number+i
            else:
                char = char + i.capitalize()
        
        # check any duplicate char are there
        if len(char) != len(set(char)):
            return False
        
        if (len(number) == 2 and len(char) == 3) or (len(number) > len(char)):
            return False

        # bothe number and char leng must be below 3 and not be zero
        if 0 < len(number) <= 3 and 0 < len(char) <= 3:
            return True

        else:
            return False
            

    def is_box_or_super(self):
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

        # special charecter check
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

        if regex.search(self.coupen_number) is not None:
            return True
        else:
            return False
    
    
    def is_contain_extra_char(self):
        """
        this method checking the coupen nuber consist any char other than A B or C
        """
        regex = re.match(r'^[ABCabc]+\d*$', self.coupen_number)
        if regex:
            return False
        else:
            return True
        


# winner announcement
class AnnounceWiners:
    """
    user given luckynumbers may be a list or in otherformat or anything.
    accept the string and convert to an array of 3 digit numbers then validate, if validated cross chck the matching to find winner
    
    mehods:
        clean: stripe all the elements except numbers
                   and returns cleanded data
        is_valied: make sure the length of taotal number count is multiples of three
        
        box_wirrers: returns box winners
        block_winners: returns box winners
        super_returns: super witters

        contest_winners : call all the three winner functions and return all winners

    """

    def __init__(self,lucky_numbers = [],luckydrawtype_id=None,context_date=None):
        self.lucky_numbers = lucky_numbers
        self.luckydrawtype_id = luckydrawtype_id
        self.context_date = context_date
        context_instance = LuckyDrawContext.objects.get(luckydrawtype_id=luckydrawtype_id,context_date=context_date)
        self.cleaned_data = []
        self.query_set = Participants.objects.filter()



    # clean input
    def clean(self):

        # Use regular expression to find three-digit numbers
        cleaned_list = re.findall(r'\d{3}', self.lucky_numbers)
        
        # make sure the array is empty, then extend the cleaced data
        self.cleaned_data = []
        self.cleaned_data.exten(cleaned_list)
        
    

    # validate
    def is_valid(self):

        """
        clean method is also enough for make a cleaned and varified data
        from the input.
        this method again going through the list and make sure all element is three digit value
        
        INFO: this function is created for future updations
              calling this function is not mendatory after 
        """

        for number in self.cleaned_data:
            if len(number) != 3:
                return False
        return True


    # announce
    def announce(self):
        """
        this fuction iterarating through all todays coupen numbers
        and varify the number is matching or not by calling one on the 
        methods(super_winner,block_winner,box_winner)
        """

        # get all participant_query_dict list and iterate through it
        # each iteration check the coupen type and call appropriate winner method
        # those methods cross match it and if there is any match, it will alter the query fields(is_winner,prize)
        all_participants = Participants.objects.filter(context_id=self.context_instance)
        
        for participant in all_participants:
            if participant.coupen_type == "SUPER":
                self.super_winner(participant)

    # super winners
    def super_winner(self,participant):
        """
        go through all provided lucky_numbers and find the match
        """
        for i in range(len(self.cleaned_data)):
            if participant.coupen_number == self.cleaned_data[i]:
                print("coupen matched update to database")

        
        

    # block winners
    def block_winner(self):
        pass


    # annownsing box winners
    def box_winner(self):
        pass




        




        