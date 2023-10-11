from itertools import permutations 
from .models import Participants
from django.db.models import Count, Sum


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
    
    # Extract the counts for each type
    box_count = next((item['count'] for item in count if item['coupen_type'] == 'BOX'), 0)
    block_count = next((item['count'] for item in count if item['coupen_type'] == 'BLOCK'), 0)
    super_count = next((item['count'] for item in count if item['coupen_type'] == 'SUPER'), 0)
    
    return {"box_count":box_count, "block_count":block_count,"super_count":super_count}


# get coupen coupen rate annoutated by coupen type\
def coupen_type_rate(query_set=None):
    """
    """
    coupen_type_rate_list = query_set.values("coupen_type").annotate(sum=Sum("coupen_rate"))

    # coupen_type_rate_list is a complex list dict compinatins
    # so se reduce it to simple key valiue pairs and return it like {"box":30, "block":45}
    reduced_dict = {}
    total_sum = 0
    for i in coupen_type_rate_list:
        reduced_dict[i["coupen_type"]] = i["sum"]
        total_sum += i["sum"]
    
    # add totol_sum also
    reduced_dict["total_sum"] = total_sum
    
    return reduced_dict
