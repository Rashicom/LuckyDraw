from django.db import models
from django.contrib.postgres.fields import ArrayField

# lucky dray type
class LuckyDraw(models.Model):
    """
    this model if for lucky draw body information, one LuckyDrawTry can have many 
    luckyDraw contexts in different dates, so luckydraw context information kept in another table
    """
    
    luckydrawtype_id = models.AutoField(primary_key=True)
    luckydraw_name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    draw_time = models.TimeField(auto_now=False, auto_now_add=False)
    


# conteced contexts under luckydraw type
class LuckyDrawContext(models.Model):
    """
    this table has a one to many relation with context type
    multiple context can conduct under a single LuckyDrawType

    only one context conduced in one date. so one only one row can be added in one date
    any data new data entry came after the lucky drow time will be added to the next date
    """

    context_id = models.AutoField(primary_key=True)
    luckydrawtype_id = models.ForeignKey(LuckyDraw, on_delete=models.CASCADE, related_name="luckydrawcontext_set")

    # date must be unique to prevent duplication, one day can have only cone context
    context_date = models.DateField()
    
    """
    list of lucky numbers announced by the organizers
    this list is provided when announsing winners and cross match according to the types
    all the given lucky number saved here for future mannual cross matching to varify the result
    """
    # array field which save all the lucky nubers for a perticular context
    context_luckynumber_list = ArrayField(models.CharField(max_length=6), null=True, blank=True)
    is_winner_announced = models.BooleanField(default=False)


# particants with lucky number
class Participants(models.Model):
    """
    Participants has one to many relation with luckydrawcontext
    multiple participants can participate under a single lucky draw
    """

    # choice for coupen type
    class CoupenType(models.TextChoices):
        BLOCK = "BLOCK"
        BOX = "BOX"
        SUPER = "SUPER"

    # choice for coupen type
    class Prizes(models.TextChoices):
        FIRST_PRIZE = "FIRST_PRIZE"
        SECOND_PRIZE = "SECOND_PRIZE"
        THIRD_PRIZE = "THIRD_PRIZE"
        FOURTH_PRIZE = "FOURTH_PRIZE"
        FIFTH_PRIZE = "FIFTH_PRIZE"
        COMPLIMENTERY_PRIZE = "COMPLIMENTERY_PRIZE"

    
    participant_id = models.AutoField(primary_key=True)
    context_id = models.ForeignKey(LuckyDrawContext, on_delete=models.CASCADE, related_name="participants_set")

    participant_name = models.CharField(max_length=50, null= True, blank= True)
    coupen_number = models.CharField(max_length=10)
    coupen_type = models.CharField(choices=CoupenType.choices, max_length=50)
    coupen_count = models.IntegerField()
    coupen_rate = models.IntegerField()
    is_winner = models.BooleanField(default=False)
    prize = models.CharField(choices=Prizes.choices, max_length=50, blank=True, null=True)
    prize_rate = models.IntegerField(blank=True,null=True)
    is_limit_exceeded = models.BooleanField(default=False)

    
 



