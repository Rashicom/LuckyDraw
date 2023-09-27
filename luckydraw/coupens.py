from .models import LuckyDraw
import re
from .models import Participants,LuckyDraw,LuckyDrawContext
from itertools import permutations

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
class AnnounceWinners:
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
        
        self.winning_prizes = []
        self.complimentery_prizes = set()
        print("constructor inetyialized")

        self.prize = ""


    # clean input
    def clean(self):
        print("clean method hit")
        # Use regular expression to find three-digit numbers
        cleaned_list = re.findall(r'\d{3}', self.lucky_numbers)
        
        # make sure the array is empty, then extend the cleaced data
        self.cleaned_data.extend(cleaned_list)

        return self.cleaned_data
        
    

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
        
        Program Flow:
            - populate winning_prizes list and complimentery_winning prizes set
            - collect all participant filtered by specific luckydraw type and date
            - iterate through the queryset and check the coupen type
            - call the appropriate method to identify the participant is a winner or not
            - these methods are responsible to update the data base of teh winnign statuses.
            - after gong through all queryset set is_winner_announced to True
        """
        print("announcing winner")
        # populating winning prizes list and complimetery winning prizes set
        self.winning_prizes.extend(self.cleaned_data[:5])
        self.complimentery_prizes.update(self.cleaned_data[5:])
        print(self.winning_prizes)
        print(self.complimentery_prizes)
        context_instance = LuckyDrawContext.objects.get(luckydrawtype_id = self.luckydrawtype_id, context_date=self.context_date)
        
        # get all participant_query_dict list and iterate through it
        # each iteration check the coupen type and call appropriate winner method
        # those methods cross match it and if there is any match, it will alter the query fields(is_winner,prize)
        all_participants = Participants.objects.filter(context_id=context_instance)
        
        for participant in all_participants:
            print("Iteration")
            # if participant.coupen_type == "SUPER":
            #     self.super_winner(participant)
            # if participant.coupen_type == "BOX":
            #     self.box_winner(participant)
            if participant.coupen_type("BLOCK"):
                self.block_winner()


        # after iteration set is_winner_announced to True and save the lucky numbers to the context_luckynumber_list


    # super winners
    def super_winner(self,participant):
        """
        go through all provided lucky_numbers and find the match
        """
        print("super winner")
        # lookup for is the number is IN  TOP 5 WINNERES or not
        for i in range(len(self.winning_prizes)):
            if self.winning_prizes[i] == participant.coupen_number:

                # seting winning prize level
                if i == 0:
                    self.prize = "FIRST_PRIZE"
                elif i == 1:
                    self.prize = "SECOND_PRIZE"
                elif i == 2:
                    self.prize = "THIRD_PRIZE"
                elif i == 3:
                    self.prize = "FOURTH_PRIZE"
                elif i == 4:
                    self.prize = "FIXTH_PRIZE"

                # update data base
                print("---------winning prize------------")
                print(self.prize)
                print(participant.coupen_number)
                # if coupen is in winner we dont wnant to ckeck the number in complimentery
                return

        # lookup for complimentery winners
        if participant.coupen_number in self.complimentery_prizes:
            print("-----------Complimentery prize----------")
            print(participant.coupen_number)

            # updte data base


    # block winners
    def block_winner(self,participant):
        """
        programm flow:
            - seperate checking based on char and number
        """
        # Regular expression to separate characters and digits
        match = re.match(r'([A-Za-z]+)([0-9]+)', participant.coupen_number)

        if match:
            characters, digits = match.groups()
            characters = characters.upper()

        # 1'ST CASE: len(characters) == len(digits) eg: ab12
        if len(characters) == len(digits):
        
            for i in len(self.cleaned_data):
                # iterate through coupen charecter
                # check any of the positional number matches
                # winner flag assert all the positons are matching not only one. eg: ab23, bothe a and b position contain2 and 3 respectivelly to win, Not a or b
                is_winner_flag = False
                for idx in characters:
                    if idx == "A":
                        if digits[0] == self.cleaned_data[i][0]:
                            is_winner_flag = True
                        else:
                            is_winner_flag = False

                    if idx == "B":
                        if digits[1] == self.cleaned_data[i][1]:
                            is_winner_flag = True
                        else:
                            is_winner_flag = False
                                
                    if idx == "C":
                        if digits[2] == self.cleaned_data[i][2]:
                            is_winner_flag = True
                        else:
                            is_winner_flag = False

                # if all the positions are perfectly marched 
                if is_winner_flag == True:

                    # figure out which winner is this
                    if i == 0:
                        self.prize = "FIRST_PRIZE"
                    elif i == 1:
                        self.prize = "SECOND_PRIZE"
                    elif i == 2:
                        self.prize = "THIRD_PRIZE"
                    elif i == 3:
                        self.prize = "FOURTH_PRIZE"
                    elif i == 4:
                        self.prize = "FIXTH_PRIZE"

                    else:
                        self.prize = "COMPLIMENTERY_PRIZE"
                    
                    # update database
                    # stop further checking
                    print("----BOX WINNER------")
                    print(self.prize)
                    print(participant.coupen_number," === ",self.cleaned_data[i])
                    return
            
        # 2'ST CASE: len(characters) > len(digits) ag: abc1
        if len(characters) > len(digits):
            
            for i in len(self.cleaned_data):
                # iterate through coupen charecter
                is_winner_flag = False
                for idx in characters:
                    if idx == "A":
                        if digits[0] == self.cleaned_data[i][0]:
                            is_winner_flag = True
                        else:
                            is_winner_flag = False

                    if idx == "B":
                        if digits[0] == self.cleaned_data[i][1]:
                            is_winner_flag = True
                        else:
                            is_winner_flag = False

                    if idx == "C":
                        if digits[0] == self.cleaned_data[i][2]:
                            is_winner_flag = True
                        else:
                            is_winner_flag = False


                # if all the positions are perfectly marched 
                if is_winner_flag == True:

                    # figure out which winner is this
                    if i == 0:
                        self.prize = "FIRST_PRIZE"
                    elif i == 1:
                        self.prize = "SECOND_PRIZE"
                    elif i == 2:
                        self.prize = "THIRD_PRIZE"
                    elif i == 3:
                        self.prize = "FOURTH_PRIZE"
                    elif i == 4:
                        self.prize = "FIXTH_PRIZE"

                    else:
                        self.prize = "COMPLIMENTERY_PRIZE"
                    
                    # update database
                    # stop further checking
                    print("----BOX WINNER------")
                    print(self.prize)
                    print(participant.coupen_number," === ",self.cleaned_data[i])
                    return

        

    # annownsing box winners
    def box_winner(self,participant):
        print("box winner")
        # we have to create a permutaion(all possible permutaions) list of the coupen number
        permutation_list = list(permutations(participant.coupen_number))

        # Convert each permutation back to an integer and save them to a list
        possible_combinations = ["".join(permutation) for permutation in permutation_list]
        print(possible_combinations)
        # iterate through possibli compinations
        for coupen in possible_combinations:
            """
            ckeck each value is in winning prizes list or in complimetery_prize list
            """
            # lookup for is the number is IN  TOP 5 WINNERES or not
            for i in range(len(self.winning_prizes)):
                if self.winning_prizes[i] == coupen:

                    # seting winning prize level
                    if i == 0:
                        self.prize = "FIRST_PRIZE"
                    elif i == 1:
                        self.prize = "SECOND_PRIZE"
                    elif i == 2:
                        self.prize = "THIRD_PRIZE"
                    elif i == 3:
                        self.prize = "FOURTH_PRIZE"
                    elif i == 4:
                        self.prize = "FIXTH_PRIZE"

                    # update data base
                    print("--------Winning prize---------")
                    print(self.prize)
                    print(coupen)
                    # if coupen is in winner we dont wnant to ckeck the number in complimentery
                    return

            # lookup for complimentery winners
            if coupen in self.complimentery_prizes:
                print("--------Complimentry prize---------")
                print(coupen)
                # updte data base
                
                # we dont want further iteration
                return

    



        




        