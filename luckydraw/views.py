from django.shortcuts import render
from django.views import View
from .forms import AddParticipantForm
from .models import LuckyDraw, LuckyDrawContext
from datetime import datetime, timedelta

# Add new participant
class AddParticipant(View):

    form_class = AddParticipantForm
    templet = "addparticipant.html"

    def post(self, request):
        """
        this metthod is creating a new participant

        accept: participant_name   optional
                coupen_number      char
                coupen_type        choice field
                luckydrawtype_id   id

        program flow:
        1 - fetch data to form and validate form
        2 - data entry time constrain checking(if data is added befere draw time, lucky drow context table instance is todays dates instance, 
                                                else it cerate a new instance for the next day and data added to that day)
        
        3 - validate coupen
        4 - update data to database
        """

        # CHECK 1 : fetching data and validatiog form
        form = self.form_class(request.POST)
        if not form.is_valid():
            return render(request,self.templet,{"error":"Please enter all fields"})


        # CHECK 2 : data entry time contrain check

        # if the time is blow draw time get or create todays dates context instance
        # if the time is high(todys context is finished and winner announced), get or create tomorrows date context instance
        
        luckydraw_instance = LuckyDraw.objects.get(luckydrawtype_id=form.changed_data.get("luckydrawtype_id"))
        draw_time = luckydraw_instance.draw_time


        # if we are entering data before drow time, data goes to todays context
        if datetime.time < draw_time:
            """
            todays context not annouced, so we can get or create todays context instance
            """
            context_instance = LuckyDrawContext.objects.get_or_create(context_date=datetime.date, luckydrawtype_id = luckydraw_instance.luckydrawtype_id)
        
        else:
            # else todays context is finished and data can will be added to the tommorrows context
            # get or create tommorrows context instance
            context_instance = LuckyDrawContext.objects.get_or_create(luckydrawtype_id = luckydraw_instance.luckydrawtype_id,context_date=datetime.date + timedelta(1))

        # CHECK 3 : validate coupen
        