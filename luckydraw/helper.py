from itertools import permutations 
from .models import Participants
from django.db.models import Count


def time_to_seconds(t):
    return t.hour * 3600 + t.minute * 60 + t.second



# find box coupen compbination count(permutations count)
def box_permutation_count(coupen_number = None):
    """
    we have to create a permutaion(all possible permutaions)
    list of the coupen number    
    """
    permutation_list = set(permutations(str(coupen_number)))
    return len(permutation_list)


# get coupen type counts
def coupen_type_counts(context_id=None):
    """
    """
    count = Participants.objects.filter(context_id = context_id).values("coupen_type").annotate(count=Count("coupen_type"))
    print(count)

