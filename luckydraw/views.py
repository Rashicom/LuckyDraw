from django.shortcuts import render
from django.views import View
from .forms import AddParticipantForm, GetorSetLuckyDrawForm, AnnounceWinnerForm, ResultsForm
from .models import LuckyDraw, LuckyDrawContext, Participants
from django.contrib.auth.decorators import login_required
from datetime import timedelta, datetime, time
from .coupens import CoupenCounter, CoupenValidator, AnnounceWinners, CoupenScraper
from .coupenfilter import WinnersFilter, DateFilter
from django.http import JsonResponse
import pytz
from .helper import time_to_seconds


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

        luckydrow_list = LuckyDraw.objects.all()

        if form.is_valid():
            print("form validated")
            form.save()
            data = {"luckydrow_list":luckydrow_list}

        else:
            
            data= {"error":form.errors, "luckydrow_list":luckydrow_list}
            print(data)
        
        
        return render(request,self.templet,data)
        
    def get(self,request):
        luckydrow_list = LuckyDraw.objects.all()
        return render(request,self.templet,{"luckydrow_list":luckydrow_list})
    
   

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
        
        print("request hitted")
        # CHECK 1 : fetching data and validatiog form
        form = self.form_class(request.POST)
        if not form.is_valid():
            print("form validation FAILED")

            return JsonResponse({"status":400,"error":"Field incomplete"})


        # CHECK 2 : data entry time contrain check

        # if the time is blow draw time get or create todays dates context instance
        # if the time is high(todys context is finished and winner announced), get or create tomorrows date context instance
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
            context_instance,_ = LuckyDrawContext.objects.get_or_create(luckydrawtype_id = luckydraw_instance,context_date=tomorow_date)

        # CHECK 3 : validate coupen
        # this coupen number is a row string , a compination of coupen number and count
        coupen_number = form.cleaned_data.get("coupen_number")
        coupen_type = form.cleaned_data.get("coupen_type")

        # CHECK 4 : seperate coupen count and coupen count and identify coupen type from coupen number
        coupen_scraper = CoupenScraper(raw_string=coupen_number, coupen_type=coupen_type)
        coupen_scraper.scrappify_coupen()

        # get cleaned values
        coupen_number = coupen_scraper.cleaned_coupen 
        coupen_type = coupen_scraper.coupen_type
        coupen_count = coupen_scraper.cleaned_coupen_count
        print(coupen_number)
        print(coupen_count)

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
                    coupen_count = coupen_count
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
class Context(View):

    Addparticipant_templet = "lucky_add.html"
    form_class = AddParticipantForm
    coupenvalidator_class = CoupenValidator

    def post(self, request, luckydrawtype_id):

        # geting lucky drow instance to pass to show the details in the frond end
        luckydrow = LuckyDraw.objects.get(luckydrawtype_id = luckydrawtype_id)
        print("request hit")
        print(luckydrow)
        # get present context participant detains to list in the html
        draw_time = datetime.strptime(str(luckydrow.draw_time), "%H:%M:%S").time()
        time_zone = pytz.timezone('Asia/Kolkata')
        time_now = datetime.now(time_zone).time()

        # find time difference to show in the frond end in any case
        time1 = time_to_seconds(time_now)
        time2 = time_to_seconds(draw_time)

        if time_now < draw_time:
            context_date = datetime.now(time_zone).date()
            time_diff = abs(time1 - time2)
            
        else:
            context_date = datetime.now(time_zone).date() + timedelta(1)
            time_diff = abs(86400 - (time1 - time2))


        contest = LuckyDrawContext.objects.filter(luckydrawtype_id=luckydrow.luckydrawtype_id, context_date=context_date)
        if contest.exists():
            # fiter participants in the contst object
            contest = contest[0]
            all_paerticipants = Participants.objects.filter(context_id= contest.context_id)
        else:
            all_paerticipants = ""
        

        # CHECK 1 : fetching data and validatiog form
        form = self.form_class(request.POST)
        if not form.is_valid():
            print("form validation FAILED")
            print(form.errors)

            return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"form not valied", "time_diff":time_diff})


        # CHECK 2 : data entry time constrain check

        # if the time is blow draw time get or create todays dates context instance
        # if the time is high(todys context is finished and winner announced), get or create tomorrows date context instance
        
        try:
            luckydraw_instance = LuckyDraw.objects.get(luckydrawtype_id=form.cleaned_data.get("luckydrawtype_id"))
        except Exception as e:
            print(e)
            return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"Not found", "time_diff":time_diff})

            
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
        
        # crossmatch with provided countimit, if user set new count limit update it
        count_limit = form.cleaned_data.get("count_limit")
        if int(context_instance.count_limit) != int(count_limit):
            context_instance.count_limit = count_limit
            context_instance.save()

        # CHECK 3 : validate coupen
        coupen_number = form.cleaned_data.get("coupen_number")
        coupen_type = form.cleaned_data.get("coupen_type")
        
        # CHECK 4 : seperate coupen count and coupen count and identify coupen type from coupen number
        coupen_scraper = CoupenScraper(raw_string=coupen_number, coupen_type=coupen_type)
        coupen_scraper.scrappify_coupen()

        # get cleaned values
        coupen_number = coupen_scraper.cleaned_coupen 
        coupen_type = coupen_scraper.coupen_type
        coupen_count = coupen_scraper.cleaned_coupen_count

        # creating instace for validator class and pass credencials
        coupen = self.coupenvalidator_class(coupen_number=coupen_number, coupen_type=coupen_type)
        

        # if coupen is valied update data base
        if coupen.is_valied():
            print("coupen validated and READY TO SAVE DATA BASE")
            
            # single coupen rate calculation
            if coupen_type=="SUPER":
                single_coupen_rate = 8
            elif coupen_type=="BOX":
                single_coupen_rate = 48
            
            else:
                # for block there is a seperate rate machanism
                number = ""
                char = ""
                for i in coupen_number:
                    if i.isnumeric():
                        number = number+i
                    else:
                        char = char + i
                
                if len(char)==1:
                    single_coupen_rate = 10.50
                elif len(char) == 2:
                    single_coupen_rate = 21
                elif len(char) == 3:
                    single_coupen_rate = 31.50
                elif len(number)==len(char):
                    single_coupen_rate = 8
            
            # calculation for limit exceeded or not
            counter = CoupenCounter(coupen_number=coupen_number,coupen_type=coupen_type,needed_count=coupen_count,context_id=context_instance.context_id)
            if counter.is_count_exceeded():
                is_limit_exceeded = True
            else:
                is_limit_exceeded = False

            # create participant with lucky number
            try:
                new_participant = Participants(
                    context_id=context_instance,
                    coupen_number = coupen_number,
                    coupen_type = coupen_type,
                    coupen_count = coupen_count,
                    coupen_rate = int(coupen_count)*float(single_coupen_rate),
                    is_limit_exceeded = is_limit_exceeded

                )
                new_participant.save()
            except Exception as e:
                print(e)
                return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"coupen not updated", "time_diff":time_diff,"contest":context_instance})


            all_paerticipants = Participants.objects.filter(context_id= context_instance.context_id)
            return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"time_diff":time_diff,"contest":context_instance})


        else:
            print("invalied coupen")
            return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"Invalied coupan", "time_diff":time_diff,"contest":context_instance})


   


    def get(self, request, luckydrawtype_id):
        """
        this method returns Add participant page

        accept: luckydrawtype_id as parmas
        """

        templet = self.Addparticipant_templet

        # geting lucky drow instance to pass to show the details in the frond end
        luckydrow = LuckyDraw.objects.get(luckydrawtype_id = luckydrawtype_id)

        # get present context participant detains to list in the html
        draw_time = datetime.strptime(str(luckydrow.draw_time), "%H:%M:%S").time()
        time_zone = pytz.timezone('Asia/Kolkata')
        time_now = datetime.now(time_zone).time()

        # calculate time diff to show
        time1 = time_to_seconds(time_now)
        time2 = time_to_seconds(draw_time)

        if time_now < draw_time:
            context_date = datetime.now(time_zone).date()
            time_diff = abs(time1 - time2)
            
        else:
            context_date = datetime.now(time_zone).date() + timedelta(1)
            time_diff = abs(86400 - (time1 - time2))

        try:
            contest = LuckyDrawContext.objects.get(luckydrawtype_id=luckydrow.luckydrawtype_id, context_date=context_date)
        except Exception as e:
            return render(request,templet,{"luckydraw":luckydrow,"time_diff":time_diff})
        
        # fiter participants in the contst object
        all_paerticipants = Participants.objects.filter(context_id= contest.context_id)

        return render(request,templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"time_diff":time_diff,"contest":contest})




# Annouce winner
class AnnounceWinner(View):
    
    form_class = AnnounceWinnerForm
    templet = "lucky_draw.html"
    coupen_filter_class = WinnersFilter
    
    def post(self, request):
        """
        this method is anouncing winners by crossmatching the given lucky number set
        and return all winner informations
        accept: lucky_numbers, luckydrawtype_id, context_date
        """
        print("ANNOUNCING WINNERES")
        # serialize and validate data
        print(request.POST)
        form = self.form_class(request.POST)
        if not form.is_valid():
            print("form not valied")
            return render(request,self.templet,{"error":"Invalid Creadencials"})
        
        # extract validate data
        luckydrawtype_id = form.cleaned_data.get('luckydrawtype_id')
        lucky_numbers = form.cleaned_data.get('lucky_numbers')
        context_date = form.cleaned_data.get('context_date')

        # CHECK 1 : context_date not grater than todays
        time_zone = pytz.timezone('Asia/Kolkata')
        today_date = datetime.now(time_zone).date()
        context_date_obj = datetime.strptime(str(context_date), "%Y-%m-%d").date()
        
        if context_date_obj > today_date:
            return render(request,self.templet,{"error":"Invalied date"})

        # CHECK 2 : never allow to perform announce winneres if the present time is less than context time
        present_time = datetime.now(time_zone).time()
        luckydraw_obj = LuckyDraw.objects.get(luckydrawtype_id=luckydrawtype_id)
        draw_time_obj = datetime.strptime(str(luckydraw_obj.draw_time), "%H:%M:%S").time()

        if present_time < draw_time_obj and context_date_obj == today_date:
            return render(request,self.templet,{"error":"Drow Time not passed"})
            

        # CHECK 3 : never allow the announcement if already announced befor
        
        try:
            context_obj = LuckyDrawContext.objects.get(luckydrawtype_id = luckydraw_obj.luckydrawtype_id, context_date=context_date)
        except Exception as e:
            return render(request,self.templet,{"error":"Context not found"})    

        # if the winner is already announced
        # if context_obj.is_winner_announced == True:
        #     print("already announced")
        #     return render(request,self.templet,{"error":"Already announced"})
        
        # ALL TEST IS PASSESD
        context_winners = AnnounceWinners(luckydrawtype_id=luckydrawtype_id, context_date=context_date, lucky_numbers=lucky_numbers)
        
        # clean data
        cleaned_data = context_winners.clean()

        # announce winners
        context_winners.announce()

        # get announced winners data
        coupen_filter = self.coupen_filter_class(luckydrawtype_id= luckydrawtype_id, context_date=context_date)
        data = coupen_filter.get_filtered_data()


        return render(request,self.templet,data)



    def get(self, request, *args, **kwargs):
        """
        retunr winner announcement page
        """
        lucky_draw = LuckyDraw.objects.all()
        contests = LuckyDrawContext.objects.values('context_date').distinct()
        
        return render(request,self.templet,{"lucky_draw":lucky_draw, "contests":contests})



class DeleteParticipant(View):
    def get(self, request, *args, **kwargs):
        participant_id = request.GET.get("participant_id")
        
        try:
            participant = Participants.objects.get(participant_id=participant_id)
            participant.delete()

        except Exception as e:
            print(e)
            return JsonResponse({"status":404})

        return JsonResponse({"status":200})




class Results(View):

    result_templet = "lucky_results.html"
    form_class = ResultsForm

    def get(self, request):

        lucky_draw = LuckyDraw.objects.all()
        return render(request,self.result_templet,{"lucky_draw":lucky_draw})


    def post(self, request):

        form = self.form_class(request.POST)
        lucky_draw = LuckyDraw.objects.all()
        print("request hit")
        # validate form
        if not form.is_valid():
            return render(request,self.result_templet, {"lucky_draw":lucky_draw,"error":"invalied date"})

        print("form validated") 
        print(form.cleaned_data)       
        # filter data by date using DateFilter class instance
        date_filter = DateFilter(
            from_date=form.cleaned_data.get("from_date"),
            to_date = form.cleaned_data.get("to_date"),
            lucky_drawtype_id=form.cleaned_data.get("lucky_drawtype_id"),

        )

        # fiter by date and return data
        data = date_filter.get_filtered_data()

        # get account detains in the selected time period
        accounts = date_filter.get_accounts()

        # return result
        return render(request, self.result_templet,{"lucky_draw":lucky_draw, **data, **accounts})
                



