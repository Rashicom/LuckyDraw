from .models import Participants, LuckyDrawContext
from django.db.models import Q
from itertools import permutations



class BaseCoupenFilter:
    pass


class WinnersFilter(BaseCoupenFilter):

    def __init__(self, luckydrawtype_id=None, context_date=None):
        self.luckydrawtype_id = luckydrawtype_id
        self.context_date = context_date
        self.data = {}
    

    def get_filtered_data(self):
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
                "participant_name": participant.participant_name,
                "coupen_type": participant.coupen_type,
                "coupen_count": participant.coupen_count,
                "prize": participant.prize,
                "prize_amnt": int(participant.coupen_count)*int(participant.prize_rate)
            }

            # appending to data lists
            self.data[prize_category].append(participant_info)

        return self.data  




class DateFilter(BaseCoupenFilter):

    def __init__(self, from_date=None, to_date=None, lucky_drawtype_id=None):
        self.from_date = from_date
        self.to_date = to_date
        self.lucky_drawtype_id = lucky_drawtype_id
        self.data = {}

    
    def get_filtered_data(self):
        """
        this method returns all winners selected between
        given time piriod
        """

        # if the lucky drow id is zero it represents retrun all lucky drow case, so we dond use lucky drow filter
        if self.lucky_drawtype_id == "ALL":
            print("return all")
            date_filter = Q(context_id__context_date__lte = self.to_date) & Q(context_id__context_date__gte = self.from_date) & Q(is_winner=True)
        else:
            date_filter = Q(context_id__context_date__lte = self.to_date) & Q(context_id__context_date__gte = self.from_date) & Q(context_id__luckydrawtype_id = self.lucky_drawtype_id) & Q(is_winner=True)

        # filter all participants under the context instance
        winning_participants = Participants.objects.filter(date_filter)
        
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
                "participant_name": participant.participant_name,
                "coupen_type": participant.coupen_type,
                "coupen_count": participant.coupen_count,
                "prize": participant.prize,
                "prize_amnt": int(participant.coupen_count)*int(participant.prize_rate)
            }

            # appending to data lists
            self.data[prize_category].append(participant_info)

        return self.data 


    def get_accounts(self):

        # if the lucky drow id is zero it represents retrun all lucky drow case, so we dond use lucky drow filter
        if self.lucky_drawtype_id == "ALL":
            date_filter = Q(context_id__context_date__lte = self.to_date) & Q(context_id__context_date__gte = self.from_date) 
        else:
            date_filter = Q(context_id__context_date__lte = self.to_date) & Q(context_id__context_date__gte = self.from_date) & Q(context_id__luckydrawtype_id = self.lucky_drawtype_id)

        # filter all participants under the context instance
        winning_participants = Participants.objects.filter(date_filter)

        accounts = {
            "box_count":0,
            "block_count":0,
            "super_count":0,

            "box_total_value":0,
            "block_total_value":0,
            "super_total_value":0,

            "total_value":0,

            "first_prize_total":0,
            "second_prize_total":0,
            "third_prize_total":0,
            "fourth_prize_total":0,
            "fifth_prize_total":0,
            "complimentary_prize_total":0,

            "total_prize":0,
            "profit":0
        }

        for i in winning_participants:
            
            if i.coupen_type == "BOX":
                # in box case the count is counpen count * coupen permutation count
                # eg: 122,10 >> count = 10 permutation count = 3 total count = 30
                # list value is the permutaion count
                permutation_count = len(set(permutations(i.coupen_number)))
                
                accounts["box_count"] += i.coupen_count * permutation_count
                accounts["box_total_value"] += i.coupen_rate
            
            elif i.coupen_type == "BLOCK":

                number = ""
                char = ""
                for j in i.coupen_number:
                    if j.isnumeric():
                        number = number+j
                    else:
                        char = char + j
                print(i.coupen_number)
                accounts["block_count"] += i.coupen_count * len(char)        # return number of combination count g: coupen ab1 count 2 total coutn = 4
                accounts["block_total_value"] += i.coupen_rate
            
            elif i.coupen_type == "SUPER":
                accounts["super_count"] += i.coupen_count 
                accounts["super_total_value"] += i.coupen_rate


            if i.is_winner and i.prize == "FIRST_PRIZE":
                accounts["first_prize_total"] += i.prize_rate * i.coupen_count

            elif i.is_winner and i.prize == "SECOND_PRIZE":
                accounts["second_prize_total"] += i.prize_rate * i.coupen_count

            elif i.is_winner and i.prize == "THIRD_PRIZE":
                accounts["third_prize_total"] += i.prize_rate * i.coupen_count

            elif i.is_winner and i.prize == "FOURTH_PRIZE":
                accounts["fourth_prize_total"] += i.prize_rate * i.coupen_count

            elif i.is_winner and i.prize == "FIFTH_PRIZE":
                accounts["fifth_prize_total"] += i.prize_rate * i.coupen_count

            elif i.is_winner and i.prize == "COMPLIMENTERY_PRIZE":
                accounts["complimentary_prize_total"] += i.prize_rate * i.coupen_count

        accounts["total_value"] = accounts["box_total_value"] + accounts["block_total_value"] + accounts["super_total_value"]
        accounts["total_prize"] = accounts["first_prize_total"] + accounts["second_prize_total"] + accounts["third_prize_total"] + accounts["fourth_prize_total"] + accounts["fifth_prize_total"] + accounts["complimentary_prize_total"]
        accounts["profit"] = accounts["total_value"] - accounts["total_prize"]

        return accounts

