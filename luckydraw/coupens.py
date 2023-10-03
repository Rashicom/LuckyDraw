from .models import LuckyDraw
import re
from .models import Participants,LuckyDraw,LuckyDrawContext
from itertools import permutations


class CoupenScraper:
    """
    this class is accpeting a string of coupen number and coupne type
    this class is for identifying coupen, coupen type and count from the coupennumber string
    
    IMPORTANT INFO: this class can handle and identify multiple row coupens and returns a list of cleaned coupens
                    dond want to create an extra thinks to add
                    in the first verion we are only providing single coupen validation
                    multiple coupen validation can be added in the next updation
    """

    def __init__(self, raw_string=None, coupen_type=None):
        self.raw_string = raw_string
        self.coupen_type = coupen_type
        self.cleaned_coupen = ""
        self.cleaned_coupen_count = 1

        
    def scrappify_coupen(self):
        """
        string contains multiple coupen numbers and counts
        this method initially check the string is a set of  block coupens or not
        then perform operations for block and super,set numbers seprarately
        """
        
        # ditits may contain coupen number and seperation specal char and count
        # eg : 1,5  254,2  897 2
        # it means we the number is wether a box or a super

        # check the string contain any letters
        if not re.search('[a-zA-Z]', self.raw_string):
            """
            if the raw string not contains any of the letters the string is consisting of
            only boc and super numbers
            """

            # Define a regular expression pattern to match the coupon and count
            pattern = r'(\d{3})(?:[^0-9]*(\d+))?'

            # Use re.findall to find all matching patterns in the input string
            matches = re.findall(pattern, self.raw_string)

            # here the coupen type is considered as the provided one
        
        else:
            """
            raw string contains letters and its a box numbers
            """
            pattern = r'([a-zA-Z0-9]+)(?:[^a-zA-Z0-9]+(\d+))?'
            # Use re.findall to find all matching patterns in the input string
            matches = re.findall(pattern, self.raw_string)

            # set coupen type as block forcefully, even the user is provided box or super
            self.coupen_type = "BLOCK"
        

        self.cleaned_coupen = matches[0][0]
        self.cleaned_coupen_count = matches[0][1] or 1
        print(self.cleaned_coupen)
        print(self.coupen_type)
        print(self.cleaned_coupen_count)
        



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

        self.prize = ""
        self.prize_rate = 0


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
            if participant.coupen_type == "SUPER":
                 self.super_winner(participant)
            if participant.coupen_type == "BOX":
                 self.box_winner(participant)
            if participant.coupen_type == "BLOCK":
                self.block_winner(participant)


        # after iteration set is_winner_announced to True and save the lucky numbers to the context_luckynumber_list
        context_instance.is_winner_announced = True
        context_instance.context_luckynumber_list = self.cleaned_data
        context_instance.save()


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
                    self.prize_rate = 5400
                elif i == 1:
                    self.prize = "SECOND_PRIZE"
                    self.prize_rate = 550
                elif i == 2:
                    self.prize = "THIRD_PRIZE"
                    self.prize_rate = 270
                elif i == 3:
                    self.prize = "FOURTH_PRIZE"
                    self.prize_rate = 120
                elif i == 4:
                    self.prize = "FIFTH_PRIZE"
                    self.prize_rate = 70
                else:
                    self.prize = "COMPLIMENTERY_PRIZE"
                    self.prize_rate = 30


                # update data base
                participant.is_winner = True
                participant.prize = self.prize
                participant.prize_rate = self.prize_rate
                participant.save()

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
            self.prize = "COMPLIMENTERY_PRIZE"
            participant.is_winner = True
            participant.prize = self.prize
            self.prize_rate = 30
            participant.prize_rate = self.prize_rate

            participant.save()


    # block winners
    def block_winner(self,participant):
        """
        programm flow:
            - seperate checking based on char and number

        WARNING: this method is designed for calculating all prizes
                  loop is limited to 1 to find first prize as per customer requirements
                  this method must be redisign to find the same in a less complex way, avoide additional complexities
        """

        print("ANNOUNCING BLOCK WINNERS")
        # Regular expression to separate characters and digits
        match = re.match(r'([A-Za-z]+)([0-9]+)', participant.coupen_number)

        if match:
            characters, digits = match.groups()
            characters = characters.upper()
            digits = str(digits)

        print(characters,digits)

        # 1'ST CASE: len(characters) == len(digits) eg: ab12
        if len(characters) == len(digits):
            print("length of chat is == len digit")
        
            # only check for first prize
            for i in range(1):
                
                # iterate through coupen charecter
                # check any of the positional number matches
                # winner flag assert all the positons are matching not only one. eg: ab23, bothe a and b position contain2 and 3 respectivelly to win, Not a or b
                is_winner_flag = False
                for idx,digit in zip(characters,digits):
                    if idx == "A":
                        if digit == str(self.cleaned_data[i])[0]:
                            is_winner_flag = True
                        else:
                            is_winner_flag = False

                    if idx == "B":
                        if digit == str(self.cleaned_data[i])[1]:
                            is_winner_flag = True
                        else:
                            is_winner_flag = False
                                
                    if idx == "C":
                        if digit == str(self.cleaned_data[i])[2]:
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
                        self.prize = "FIFTH_PRIZE"

                    else:
                        self.prize = "COMPLIMENTERY_PRIZE"
                    
                    # update database
                    participant.is_winner = True
                    participant.prize = self.prize
                    participant.save()

                    # stop further checking
                    print("----BOX WINNER------")
                    print(self.prize)
                    print(participant.coupen_number," === ",self.cleaned_data[i])
                    return
            
        # 2'ST CASE: len(characters) > len(digits) ag: abc1
        elif len(characters) > len(digits):
            
            # only check for first prize
            for i in range(1):
                
                # iterate through coupen charecter
                is_winner_flag = False
                for idx in characters:
                    
                    if idx == "A":
                        if digits[0] == str(self.cleaned_data[i])[0]:
                            is_winner_flag = True
                            break

                    if idx == "B":
                        if digits[0] == str(self.cleaned_data[i][1]):
                            is_winner_flag = True
                            break

                    if idx == "C":
                        if digits[0] == str(self.cleaned_data[i][2]):
                            is_winner_flag = True
                            break


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
                        self.prize = "FIFTH_PRIZE"

                    else:
                        self.prize = "COMPLIMENTERY_PRIZE"
                    
                    # update database
                    participant.is_winner = True
                    participant.prize = self.prize
                    participant.save()

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
                        self.prize_rate = 5400
                    elif i == 1:
                        self.prize = "SECOND_PRIZE"
                        self.prize_rate = 550
                    elif i == 2:
                        self.prize = "THIRD_PRIZE"
                        self.prize_rate = 270
                    elif i == 3:
                        self.prize = "FOURTH_PRIZE"
                        self.prize_rate = 120
                    elif i == 4:
                        self.prize = "FIFTH_PRIZE"
                        self.prize_rate = 70
                    else:
                        self.prize = "COMPLIMENTERY_PRIZE"
                        self.prize_rate = 30

                    # update data base
                    participant.is_winner = True
                    participant.prize = self.prize
                    participant.prize_rate = self.prize_rate
                    participant.save()

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
                self.prize = "COMPLIMENTERY_PRIZE"
                self.prize_rate = 30
                participant.is_winner = True
                participant.prize = self.prize
                participant.prize_rate = self.prize_rate

                participant.save()

                # we dont want further iteration
                return




class WinnersFilter:

    def __init__(self, luckydrawtype_id=None, context_date=None):
        self.luckydrawtype_id = luckydrawtype_id
        self.context_date = context_date
        self.data = {}
    

    def getcontext_and_validate(self):
        """
        this checks the context is exist or not
        if exist make sure that the context is already announced
        """

        context_instance = LuckyDrawContext.objects.filter(luckydrawtype_id=self.luckydrawtype_id, context_date=self.context_date)
        
        # does not exist if context doex not fount
        if not context_instance.exists():
            raise Exception("Context does not found")
        else:
            context_instance = context_instance[0]

        # check the winners is announce or not
        if context_instance.is_winner_announced == False:
            raise Exception("Winners not announced yet")

        # filter all participants under the context instance
        winning_participants = Participants.objects.filter(context_id=context_instance.context_id, is_winner=True)
        
        # initilize
        self.data = {
            "FIRST_PRIZE": [],
            "SECOND_PRIZE": [],
            "THIRD_PRIZE": [],
            "FOURTH_PRIZE": [],
            "FIFTH_PRIZE": [],
            "COMPLIMENTERY_PRIZE": [],
        }

        # iterate throuhg participants
        for participant in winning_participants:
            prize_category = participant.prize
            participant_info = {
                "coupen_number": participant.coupen_number,
                "coupen_type": participant.coupen_type,
                "coupen_count": participant.coupen_count,
                "prize": participant.prize,
                "prize_amnt": int(participant.coupen_count)*int(participant.prize_rate)
            }

            # appending to data lists
            self.data[prize_category].append(participant_info)

        return self.data  



# coupen counter for seperate limit exceeded coupens
class CoupenCounter:
    
    def __init__(self,coupen_number = None,coupen_type = None, context_id=None,needed_count=None):
        self.coupen_type = coupen_type
        self.context_id = context_id
        self.needed_count = needed_count
        
        # if coupen type is box, there are 6 compinations
        # we form a set of 6 compinations to reduce the complexity when we perform search
        if coupen_type=="BOX":
            # we have to create a permutaion(all possible permutaions) list of the coupen number
            permutation_list = list(permutations(str(coupen_number)))

            # Convert each permutation back to an integer and save them to a list
            possible_combinations = ["".join(permutation) for permutation in permutation_list]
            self.coupen_number = set(possible_combinations)
        
        else:
            self.coupen_number = set()
            self.coupen_number.add(str(coupen_number))

        self.query_set = Participants.objects.filter(context_id=self.context_id).values_list("coupen_number","coupen_count","is_limit_exceeded")


    def is_count_exceeded(self):
        count = 0
        for participant in self.query_set:
            
            if participant[0] in self.coupen_number:
                # if participant limit set to true already, it means its count already exceeded before
                # so we dond want to loop more return True
                
                if participant[2] == True:
                    return True
                count += int(participant[1])
            

        # check needed count is exceede or not
        count += int(self.needed_count)
        
        # match with count limit user set.
        context = LuckyDrawContext.objects.get(context_id=self.context_id)
        
        if int(count) >= int(context.count_limit):
            return True
        else:
            return False
        

        
        






        

