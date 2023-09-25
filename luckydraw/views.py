from django.shortcuts import render
from django.views import View
from .forms import AddParticipantForm, GetorSetLuckyDrawForm
from .models import LuckyDraw, LuckyDrawContext, Participants
from django.contrib.auth.decorators import login_required
from datetime import timedelta, datetime, time
from .coupens import CoupenValidator
from django.http import JsonResponse
import pytz



class GetorSetLuckyDraw(View):
    """
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
        print("request hit")
        form = self.form_class(request.POST)
        if form.is_valid():
            print("form validated")
            form.save()
            message = {}

        else:
            
            message = {"error":form.errors}
            print(message)
        
        return render(request,self.templet,message)
    
   

# Add new participant ajax call
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

            return JsonResponse({"status":400,"error":"Field incomplete"})


        # CHECK 2 : data entry time contrain check

        # if the time is blow draw time get or create todays dates context instance
        # if the time is high(todys context is finished and winner announced), get or create tomorrows date context instance
        print(form.cleaned_data.get("coupen_count"))
        try:
            luckydraw_instance = LuckyDraw.objects.get(luckydrawtype_id=form.cleaned_data.get("luckydrawtype_id"))
        except Exception as e:
            print(e)
            return JsonResponse({"status":400,"error":"no lucky drow found"})
            
        draw_time = luckydraw_instance.draw_time
        
        # drow time is a string, so we have to convert it to time object
        draw_time_obj = datetime.strptime(str(draw_time), "%H:%M:%S").time()
        
        # to know the current time we have to make a time zone object
        time_zone = pytz.timezone('Asia/Kolkata')

        # if we are entering data before drow time, data goes to todays context
        if datetime.now(time_zone).time() < draw_time_obj:
            print("context : today")
            """
            todays context not annouced, so we can get or create todays context instance
            """
            context_instance,_ = LuckyDrawContext.objects.get_or_create(context_date=datetime.now(time_zone).date(), luckydrawtype_id = luckydraw_instance)
        
        else:
            # else todays context is finished and data can will be added to the tommorrows context
            # get or create tommorrows context instance
            print("context: tommorow")
            tomorow_date = datetime.now(time_zone).date()+timedelta(1)
            print(tomorow_date)
            context_instance,_ = LuckyDrawContext.objects.get_or_create(luckydrawtype_id = luckydraw_instance,context_date=tomorow_date)

        # CHECK 3 : validate coupen
        coupen_number = form.cleaned_data.get("coupen_number")
        coupen_type = form.cleaned_data.get("coupen_type")
        
        # creating instace for validator class and pass credencials
        coupen = self.coupenvalidator_class(coupen_number=coupen_number, coupen_type=coupen_type)
        
        # if coupen is valied update data base
        if coupen.is_valied():
            print("coupen validated and READY TO SAVE DATA BASE")
            # create participant with lucky number
            try:
                new_participant = Participants(
                    context_id=context_instance,
                    coupen_number = coupen_number,
                    coupen_type = coupen_type,
                    coupen_count = form.cleaned_data.get("coupen_count")
                )
                new_participant.save()
            except Exception as e:
                print(e)
                return JsonResponse({"status":500,"message":"success"})


            return JsonResponse({"status":201,"message":"success"})


        else:
            print("invalied coupen")
            return JsonResponse({"status":400,"error":"invalid coupen"})


    


# get context
class GetContext(View):

    Addparticipant_templet = "addparticipant.html"

   
    def get(self, request, luckydrawtype_id):
        """
        this method returns Add participant page

        accept: luckydrawtype_id as parmas
        """

        templet = self.Addparticipant_templet

        # geting lucky drow instance to pass to show the details in the frond end
        luckydrow = LuckyDraw.objects.get(luckydrawtype_id = luckydrawtype_id)

        return render(request,templet,{"luckydraw":luckydrow})


