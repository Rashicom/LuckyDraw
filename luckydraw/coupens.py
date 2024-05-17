from .models import LuckyDraw
import re
from .models import Participants,LuckyDraw,LuckyDrawContext
from itertools import permutations
from datetime import datetime

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
            only box and super numbers
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
        
        context_instance = LuckyDrawContext.objects.get(luckydrawtype_id = self.luckydrawtype_id, context_date=self.context_date)
        
        # get all participant_query_dict list and iterate through it
        # each iteration check the coupen type and call appropriate winner method
        # those methods cross match it and if there is any match, it will alter the query fields(is_winner,prize)
        all_participants = Participants.objects.filter(context_id=context_instance)
        
        for participant in all_participants:
            print(participant.coupen_number)

            # additional checking for super, bcz super contains 
            if participant.coupen_type == "SUPER":
                number = ""
                char = ""
                for i in participant.coupen_number:
                    if i.isnumeric():
                        number = number+i
                    else:
                        char = char + i

                # pure super check
                if len(char) == 0:
                    self.super_winner(participant)
                # partial block: eg: AB12
                if len(number)==len(char):
                    self.block_winner(participant)

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

                # if coupen is in winner we dont wnant to ckeck the number in complimentery
                return

        # lookup for complimentery winners
        if participant.coupen_number in self.complimentery_prizes:

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

        # Regular expression to separate characters and digits
        match = re.match(r'([A-Za-z]+)([0-9]+)', participant.coupen_number)

        if match:
            characters, digits = match.groups()
            characters = characters.upper()
            digits = str(digits)

        # fetching first lucky number form the cleaned data
        # block is only applicable for first prize
        first_prize_number = str(self.cleaned_data[0])

        # 1'ST CASE: len(characters) == len(digits) eg: ab12
        if len(characters) == len(digits) and len(characters) > 1:
            
            # iterate through coupen charecter
            # check any of the positional number matches
            # winner flag assert all the positons are matching not only one. eg: ab23, bothe a and b position contain2 and 3 respectivelly to win, Not a or b
            is_winner_flag = False
            for idx,digit in zip(characters,digits):
                if idx == "A":
                    if digit == first_prize_number[0]:
                        is_winner_flag = True
                    else:
                        is_winner_flag = False
                        break
                elif idx == "B":
                    if digit == first_prize_number[1]:
                        is_winner_flag = True
                    else:
                        is_winner_flag = False
                        break
                            
                elif idx == "C":
                    if digit == first_prize_number[2]:
                        is_winner_flag = True
                    else:
                        is_winner_flag = False
                        break
            # if all the positions are perfectly marched 
            if is_winner_flag == True:
                
                self.prize = "FIRST_PRIZE"

                # update database
                participant.is_winner = True
                participant.prize = self.prize
                participant.prize_rate = 700
                participant.save()
                return
            return
                
            
        # 2'ST CASE: len(characters) > len(digits) or len(char) == 1 ag: abc1
        else:
                
            # iterate through coupen charecter
            is_winner_flag = False
            match_count = 0
            for idx in characters:
                
                if idx == "A":
                    if digits[0] == first_prize_number[0]:
                        is_winner_flag = True
                        match_count += 1
                        
                elif idx == "B":
                    if digits[0] == first_prize_number[1]:
                        is_winner_flag = True
                        match_count += 1
                elif idx == "C":
                    if digits[0] == first_prize_number[2]:
                        is_winner_flag = True
                        match_count += 1
            # if all the positions are perfectly marched 
            if is_winner_flag == True:
                
                self.prize = "FIRST_PRIZE"

                # update database
                participant.is_winner = True
                participant.prize = self.prize
                participant.prize_rate = match_count * 100
                participant.save()
                # stop further checking
                return
            return
            
        

    # annownsing box winners
    def box_winner(self,participant):
        print("box winner")
        # we have to create a permutaion(all possible permutaions) list of the coupen number
        permutation_list = list(permutations(participant.coupen_number))

        # Convert each permutation back to an integer and save them to a list
        possible_combinations = ["".join(permutation) for permutation in permutation_list]

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

                    # if coupen is in winner we dont wnant to ckeck the number in complimentery
                    return

            # lookup for complimentery winners
            if coupen in self.complimentery_prizes:

                # updte data base
                self.prize = "COMPLIMENTERY_PRIZE"
                self.prize_rate = 30
                participant.is_winner = True
                participant.prize = self.prize
                participant.prize_rate = self.prize_rate

                participant.save()

                # we dont want further iteration
                return




# coupen counter for seperate limit exceeded coupens
class CoupenCounter:
    
    def __init__(self,coupen_number = None,coupen_type = None, context_id=None,needed_count=None):
        self.coupen_type = coupen_type
        self.context_id = context_id
        self.needed_count = needed_count

        # exceeded and available coupen counts
        self.countlimit_exceeded = None
        self.available_count = None
        
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

        self.query_set = Participants.objects.filter(context_id=self.context_id,coupen_type=self.coupen_type).values_list("coupen_number","coupen_count","is_limit_exceeded")


    def is_count_exceeded(self):
        count = 0
        for participant in self.query_set:
            
            if participant[0] in self.coupen_number:
                # participant[0] is coupen_number
                # if participant limit set to true already, it means its count already exceeded before
                # so we dont want to loop more, return True
                
                if participant[2] == True:
                    # participant[2] == is_limit_exceeded

                    # if the limit is already exceeded all the needed count is exceeded count
                    self.countlimit_exceeded = self.needed_count
                    return True
                
                count += int(participant[1])
                # participant[1] == coupen count

        # check needed count is exceede or not
        count += int(self.needed_count)
        
        # match with count limit user set.
        context = LuckyDrawContext.objects.get(context_id=self.context_id)
        
        if int(count) > int(context.count_limit):
            """
            set avalilable count and exceeded count for further processing
            available count : count which can be updated without count limit exceeded
            exceeded count : balance count considered as exceeded count
            """
        
            self.countlimit_exceeded = int(count) - int(context.count_limit)
            self.available_count = int(self.needed_count) - self.countlimit_exceeded
            
            return True
        else:
            self.available_count = self.needed_count
            return False
        


# bulk coupen generator
class CoupenExtractor:
    def __init__(self):

        # all message lines except data time fields
        self.message_lines = []

        # coupen and count extracted and filtered and saved in format [[coupen,count],[]..]
        self.super_coupen = []
        self.block_coupen = []
        self.box_coupens = []
        self.unmatched_message_lines = []
        self.block_pattern = r'([a-cA-C]+[0-9]+)(?:[^a-cA-C0-9]+(\d+))?'
        self.super_pattern = r'(?<!abc)(?<!ab)(?<!ac)(?<!bc)(?<!ABC)(?<!AB)(?<!AC)(?<!BC)(?<!a)(?<!b)(?<!c)(?<!A)(?<!B)(?<!C)(\d{3})(?:[^0-9]*(\d+))?'
        


    def feed_file(self, file_obj=None, date_from=None, date_to=None):
        """
            Read the file and fetch the message and save in in message_lines list
            only messages which is in between date_from and date_to are saved   NEED TO IMPLIMNT
        """
        
        # regex for fetching list of messages
        pattern = r"(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - ([^:]+): (.*)"
        
        
        with file_obj.open() as file:
            data = file.readlines()

        # fetching messages only
        for message in data:
            message = message.decode("utf-8")
            match = re.match(pattern, message)

            if match:
                date = match.group(1)
                time = match.group(2)
                date_time_obj = datetime.strptime(f"{date} {time}","%d/%m/%Y %H:%M")
                
                message_from = match.group(3)
                message_content = match.group(4)
                self.message_lines.append(message_content)
            else:
                message_content = message
                self.message_lines.append(message_content)

    def get_all_coupens(self):
        return self.super_coupen + self.box_coupens + self.block_coupen
    
    def classify_coupens(self):
        """
        Iterate through the self.message_lines and extract coupens and count then classify it
        """
        
        # go through all lines and extract coupen and count
        for line in self.message_lines:

            """----------------BLOCK SEARCH-------------------"""
            # pattern
            matches = re.findall(self.block_pattern, line)

            # go through all matches
            for match in matches:
                # split coupen into sigle if coupen is grouped
                # eg: b124 4 >> b1 4,b2 4,b4 4
                coupen = match[0]
                groupe_pattern = r'\b[a-cA-C]\d{2,}\b'
                groupe_matches = re.findall(groupe_pattern, coupen)
                if groupe_matches:
                    grouped_coupen = groupe_matches[0]
                    pairs = re.findall(r'([a-zA-Z])(\d+)', grouped_coupen)
                    letter = pairs[0][0]
                    grouped_digits = pairs[0][1]
                    # iterate throuhg digit and create coupen and update it
                    for digit in grouped_digits:
                        self.block_coupen.append(("BLOCK",letter+digit,1 if match[1]=="" else match[1]))
                else:
                    self.block_coupen.append(("BLOCK",match[0],1 if match[1]=="" else match[1]))
                    

            """----------------SUPER AND BOX SEARCH-------------------"""
            # pattern
            matches = re.findall(self.super_pattern, line)

            # go through all matches
            if "BOX" in line.upper():
                for match in matches:
                    self.box_coupens.append(("BOX",match[0],1 if match[1]=="" else match[1]))
            else:
                for match in matches:
                    self.super_coupen.append(("SUPER",match[0],1 if match[1]=="" else match[1]))


