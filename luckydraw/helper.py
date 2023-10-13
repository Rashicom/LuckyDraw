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
    its returning the count of coupen types
    """
    filtered_counts = Participants.objects.filter(context_id = context_id).values("coupen_type").annotate(count=Sum("coupen_count"))
    print(filtered_counts)
    data_dict = {}
    for type_count in filtered_counts:
        data_dict[type_count["coupen_type"]] = type_count["count"]

    return {"box_count":data_dict.get("BOX",0), "block_count":data_dict.get("BLOCK",0),"super_count":data_dict.get("SUPER",0)}


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
