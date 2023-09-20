from django.db import models


# lucky dray type
class LuckyDrawType(models.Model):
    """
    this model if for lucky draw body information, one LuckyDrawTry can have many 
    luckyDraw contexts in different dates, so luckydraw context information kept in another table
    """
    
    luckydraw_id = models.AutoField(primary_key=True)

    luckydraw_name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    created_on = models.DateField(auto_now=True, auto_now_add=False)


# conteced contexts under luckydraw type
class LuckyDrawContext(models.Model):
    """
    this table has a one to many relation with context type
    multiple context can conduct under a single LuckyDrawType
    """

    context_id = models.AutoField(primary_key=True)
    luckydraw_id = models.ForeignKey(LuckyDrawType, on_delete=models.CASCADE, related_name="luckydrawcontext_set")

    context_name = models.CharField(max_length=50)
    context_date = models.DateField(auto_now=True, auto_now_add=False)
    context_time = models.TimeField(auto_now=False, auto_now_add=False)
    description = models.TextField(null=True, blank=True)


# particants with lucky number
class Participants(models.Model):
    """
    Participants has one to many relation with luckydrawcontext
    multiple participants can participate under a single lucky draw

    WARNING: lucky_number type and uniqueness clarification needed
    """

    participant_id = models.AutoField(primary_key=True)
    context_id = models.ForeignKey(LuckyDrawContext, on_delete=models.CASCADE, related_name="participants_set")

    # lucky drow number must be unique under context only
    # check compaingned uniquness lucky_number,context_id
    # require client clarification
    lucky_number = models.CharField(max_length=50, unique=True)
    participant_name = models.CharField(max_length=50, null= True, blank= True)
    is_winner = models.BooleanField(default=False)



class ContextWinner(models.Model):
    """
    ContextWinner has one to many relation with LuckyDrawContext, one context may have multiple winners
    also one to many relation with participant, one participant my be a winner from two or more contexts

    WARNING: due to the one to many relation with participant table, duplicating one participant entry not restricted
             In this case one context may contain two same winner. To make sure other functionalities like one user may be a winner from
             different contexts or same context but contected in defferent dates, we cant put a uniqunes constraint here
             
             mentioned duplication problom is a side effect of this

             So duplication enrty from a single context MUST BE PREVENTED IN THE VIEWS BUISINESS LOGIC
    """

    winner_id = models.AutoField(primary_key=True)
    context_id = models.ForeignKey(LuckyDrawContext, on_delete=models.CASCADE, related_name="contextwinner_set")
    participant_id = models.ForeignKey(Participants, on_delete=models.CASCADE, related_name="contextwinner_set")