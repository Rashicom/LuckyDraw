from django.shortcuts import render
from django.views import View
from .forms import AddParticipantForm, GetorSetLuckyDrawForm
from .models import LuckyDraw, LuckyDrawContext
from datetime import datetime, timedelta
from .coupens import CoupenValidator
from django.http import JsonResponse



class GetorSetLuckyDraw(View):
    """
    ACCESS: ADMIN ONLY
    """

    form_class = GetorSetLuckyDrawForm
    templet = "adminhome.html"

    def post(self, request):
        """
        creating new lucky draw
        accept: luckydraw_name
                description       optional
                draw_time
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            message = {}

        else:
            
            message = {"error":form.errors}
            print(message)
        
        return render(request,self.templet,message)
    

    def get(self, request):
        """
        return admin home page
        """
        luckydrow_list = LuckyDraw.objects.all()
        return render(request,self.templet,{"luckydrow_list":luckydrow_list})


# Add new participant
class AddParticipant(View):

    form_class = AddParticipantForm
    coupenvalidator_class = CoupenValidator

    def post(self, request):
        """
        this metthod is creating a new participant ajax call

        accept: participant_name   optional
                coupen_number      char
                coupen_type        choice field
                coupen_count       integer
                luckydrawtype_id   id

        program flow:
        1 - fetch data to form and validate form
        2 - data entry time constrain checking(if data is added befere draw time, lucky drow context table instance is todays dates instance, 
                                                else it cerate a new instance for the next day and data added to that day)
        
        3 - validate coupen
        4 - update data to database
        """
        
        print("request hit")
        # CHECK 1 : fetching data and validatiog form
        form = self.form_class(request.POST)
        if not form.is_valid():
            print("form validation FAILED")
            return JsonResponse({"error":"Please enter a valid data"})


        # CHECK 2 : data entry time contrain check

        # if the time is blow draw time get or create todays dates context instance
        # if the time is high(todys context is finished and winner announced), get or create tomorrows date context instance
        
        try:
            luckydraw_instance = LuckyDraw.objects.get(luckydrawtype_id=form.changed_data.get("luckydrawtype_id"))
        except Exception as e:
            print(e)
            return JsonResponse({"error":"not lucky drow found"})
            
        draw_time = luckydraw_instance.draw_time


        # if we are entering data before drow time, data goes to todays context
        if datetime.time < draw_time:
            print("context : today")
            """
            todays context not annouced, so we can get or create todays context instance
            """
            context_instance = LuckyDrawContext.objects.get_or_create(context_date=datetime.date, luckydrawtype_id = luckydraw_instance.luckydrawtype_id)
        
        else:
            # else todays context is finished and data can will be added to the tommorrows context
            # get or create tommorrows context instance
            print("context: tommorow")
            context_instance = LuckyDrawContext.objects.get_or_create(luckydrawtype_id = luckydraw_instance.luckydrawtype_id,context_date=datetime.date + timedelta(1))

        # CHECK 3 : validate coupen
        coupen_number = form.cleaned_data.get("coupen_number")
        coupen_type = form.cleaned_data.get("coupen_type")
        
        # creating instace for validater class and pass credencials
        coupen = self.coupenvalidator_class(coupen_number=coupen_number, coupen_type=coupen_type)
        
        # if coupen is valied update data base
        if coupen.is_valied():
            print("coupen validated and READY TO SAVE DATA BASE")
            return JsonResponse({"status":201,"message":"success"})


        else:
            print("invalied coupen")
            return JsonResponse({"status":"400","error":"invalied coupen"})



