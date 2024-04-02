from django.shortcuts import render, redirect
from django.views import View
from .forms import AddParticipantForm, GetorSetLuckyDrawForm, AnnounceWinnerForm, ResultsForm, UserReportForm, WinnerAnnouncementPdfForm, AdditionalBillingReportForm, AdditionalBillingReportPdfForm
from .models import LuckyDraw, LuckyDrawContext, Participants
from django.contrib.auth.decorators import login_required
from datetime import timedelta, datetime, time
from .coupens import CoupenCounter, CoupenValidator, AnnounceWinners, CoupenScraper
from .coupenfilter import WinnersFilter, DateFilter
from django.http import JsonResponse
import pytz
from .helper import time_to_seconds, box_permutation_count, coupen_type_counts,coupen_type_rate
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .pdf import generate_pdf, generate_winner_pdf, generate_resultreport_pdf, generate_pdf_from_html
from django.http import FileResponse
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt



class GetorSetLuckyDraw(View):
    """
    """
    form_class = GetorSetLuckyDrawForm
    templet = "adminhome.html"

    @method_decorator(login_required(login_url="login"))
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

    @method_decorator(login_required(login_url="login"))
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


    


# get and post context
class Context(View):
    
    Addparticipant_templet = "lucky_add.html"
    form_class = AddParticipantForm
    coupenvalidator_class = CoupenValidator

    @method_decorator(login_required(login_url="login"))
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

            # coupen wise count to show in html
            coupen_typewise_count = coupen_type_counts(context_id = contest.context_id)
        
        else:
            # no cpontext fount means this is the first data
            # if there is no contest fount set participants and coupen counts to null/0
            coupen_typewise_count = {"box_count":0, "block_count":0,"super_count":0}
            all_paerticipants = ""
        

        # CHECK 1 : fetching data and validatiog form
        form = self.form_class(request.POST)
        if not form.is_valid():
            print("form validation FAILED")
            return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"Invalied fields", "time_diff":time_diff, **coupen_typewise_count})
        

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


        """------------THIS AUTO DATE SETTING IS TURNING OFFED FOR TEST USE ------------"""
        # if we are entering data before drow time, data goes to todays context
        if datetime.now(time_zone).time() < draw_time_obj:
            print("context : today")
            """
            todays context not annouced, so we can get or create todays context instance
            """
            # TURN OFFED
            # context_instance,_ = LuckyDrawContext.objects.get_or_create(context_date=datetime.now(time_zone).date(), luckydrawtype_id = luckydraw_instance)
            

        else:
            # else todays context is finished and data can will be added to the tommorrows context
            # get or create tommorrows context instance
            print("context: tommorow")
            tomorow_date = datetime.now(time_zone).date()+timedelta(1)
            print(tomorow_date)

            # TURN OFFED
            # context_instance,_ = LuckyDrawContext.objects.get_or_create(luckydrawtype_id = luckydraw_instance,context_date=tomorow_date)
        
        # in all cases the coupen is added todays contest
        context_instance,_ = LuckyDrawContext.objects.get_or_create(context_date=datetime.now(time_zone).date(), luckydrawtype_id = luckydraw_instance)
        """-------------------------------------------------------------------------------"""

        # crossmatch with provided countimit, if user set new count limit update it
        count_limit = form.cleaned_data.get("count_limit")
        if int(context_instance.count_limit) != int(count_limit):
            context_instance.count_limit = count_limit
            context_instance.save()

        # CHECK 3 : validate coupen
        coupen_number = form.cleaned_data.get("coupen_number")
        coupen_type = form.cleaned_data.get("coupen_type")
        participant_name = form.cleaned_data.get("participant_name")

        # CHECK 4 : seperate coupen count and coupen count and identify coupen type from coupen number
        coupen_scraper = CoupenScraper(raw_string=coupen_number, coupen_type=coupen_type)
        coupen_scraper.scrappify_coupen()

        # get cleaned values
        coupen_number = coupen_scraper.cleaned_coupen 
        coupen_type = coupen_scraper.coupen_type
        coupen_count = coupen_scraper.cleaned_coupen_count

        if int(coupen_count) == 0:
            return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"Invalied count", "time_diff":time_diff,"contest":context_instance,**coupen_typewise_count})

        # creating instace for validator class and pass credencials
        coupen = self.coupenvalidator_class(coupen_number=coupen_number, coupen_type=coupen_type)
        

        # if coupen is valied update data base
        if coupen.is_valied():
            print("coupen validated and READY TO SAVE DATA BASE")
            
            # single coupen rate calculation
            if coupen_type=="SUPER":
                single_coupen_rate = 8
            elif coupen_type=="BOX":
                """
                here may be the coupen contains 2 same digits in, this case there is no 6 compinations
                we have to find the coupen rate according to the compbinations
                """
                permutation_count = box_permutation_count(coupen_number=coupen_number)
                single_coupen_rate = int(permutation_count) * 8
            
            else:
                # for block there is a seperate rate machanism
                number = ""
                char = ""
                for i in coupen_number:
                    if i.isnumeric():
                        number = number+i
                    else:
                        char = char + i
                
                if len(char)==1 and len(number) == 1:
                    single_coupen_rate = 10.50

                elif len(char) > len(number):
                    single_coupen_rate = 10.5 * len(char)

                elif len(number)==len(char):
                    single_coupen_rate = 8
                    coupen_type = "SUPER"  # overridding the type to super if the value is 8
            
            # calculation for limit exceeded or not
            counter = CoupenCounter(coupen_number=coupen_number,coupen_type=coupen_type,needed_count=coupen_count,context_id=context_instance.context_id)
            
            if counter.is_count_exceeded():
                """
                if the count limit is exceeded we have to save tocken with limited avalilable count
                rest of the count is added as a seperate row as is count_limit_exceeded as True
                """
                countlimit_exceeded = counter.countlimit_exceeded

                # create participant with lucky number
                try:
                    new_participant = Participants(
                        context_id=context_instance,
                        participant_name = participant_name,
                        coupen_number = coupen_number,
                        coupen_type = coupen_type,
                        coupen_count = countlimit_exceeded,
                        coupen_rate = int(countlimit_exceeded)*float(single_coupen_rate),
                        is_limit_exceeded = True

                    )
                    new_participant.save()

                except Exception as e:
                    print(e)
                    return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"coupen not updated", "time_diff":time_diff,"contest":context_instance,"last_participant_name":participant_name, **coupen_typewise_count})
                
            


            if counter.available_count is not None:

                # create participant with lucky number
                try:
                    new_participant = Participants(
                        context_id=context_instance,
                        participant_name = participant_name,
                        coupen_number = coupen_number,
                        coupen_type = coupen_type,
                        coupen_count = counter.available_count,
                        coupen_rate = int(counter.available_count)*float(single_coupen_rate),
                        is_limit_exceeded = False

                    )
                    new_participant.save()

                except Exception as e:
                    print(e)
                    return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"coupen not updated", "time_diff":time_diff,"contest":context_instance,"last_participant_name":participant_name, **coupen_typewise_count})


            all_paerticipants = Participants.objects.filter(context_id= context_instance.context_id)
            # coupen wise count to show in html
            coupen_typewise_count = coupen_type_counts(context_id = context_instance.context_id)
            return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"time_diff":time_diff,"contest":context_instance,"last_participant_name":participant_name, **coupen_typewise_count})


        else:
            print("invalied coupen")
            return render(request,self.Addparticipant_templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"error":"Invalied coupan", "time_diff":time_diff,"contest":context_instance,"last_participant_name":participant_name, **coupen_typewise_count})


   
    @method_decorator(login_required(login_url="login"))
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
            # auto fetching using time feature is TURNED OFF
            # contest = LuckyDrawContext.objects.get(luckydrawtype_id=luckydrow.luckydrawtype_id, context_date=context_date)
            # FOR TEST PORPOSE returns todays contes, we dont want to return tommorrows contest if drow time not passed
            contest = LuckyDrawContext.objects.get(luckydrawtype_id=luckydrow.luckydrawtype_id, context_date=datetime.now(time_zone).date())
        except Exception as e:
            return render(request,templet,{"luckydraw":luckydrow,"time_diff":time_diff})
        
        # fiter participants in the contst object
        all_paerticipants = Participants.objects.filter(context_id= contest.context_id)
        
        #coupen count
        coupen_typewise_count = coupen_type_counts(context_id = contest.context_id)
         
        return render(request,templet,{"luckydraw":luckydrow, "all_paerticipants":all_paerticipants,"time_diff":time_diff,"contest":contest, **coupen_typewise_count})




# Annouce winner
class AnnounceWinner(View):
    
    form_class = AnnounceWinnerForm
    templet = "lucky_draw.html"
    coupen_filter_class = WinnersFilter
    
    @method_decorator(login_required(login_url="login"))
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
        
        # if context_date_obj > today_date:
        #     return render(request,self.templet,{"error":"Invalied date"})

        # CHECK 2 : never allow to perform announce winneres if the present time is less than context time
        present_time = datetime.now(time_zone).time()
        luckydraw_obj = LuckyDraw.objects.get(luckydrawtype_id=luckydrawtype_id)
        draw_time_obj = datetime.strptime(str(luckydraw_obj.draw_time), "%H:%M:%S").time()

        # if present_time < draw_time_obj and context_date_obj == today_date:
        #     return render(request,self.templet,{"error":"Drow Time not passed"})
            

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


    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        """
        retunr winner announcement page
        """
        lucky_draw = LuckyDraw.objects.all()
        contests = LuckyDrawContext.objects.values('context_date').distinct().order_by('-context_date')
        
        return render(request,self.templet,{"lucky_draw":lucky_draw, "contests":contests})




class DeleteParticipant(View):

    @method_decorator(login_required(login_url="login"))
    def get(self, request, *args, **kwargs):
        participant_id = request.GET.get("participant_id")
        
        try:
            participant = Participants.objects.get(participant_id=participant_id)
            participant.delete()
        
        except Exception as e:
            print(e)
            return JsonResponse({"status":404})
        return JsonResponse({"status":200,"coupen_type":participant.coupen_type})




class Results(View):

    result_templet = "result_reports.html"
    form_class = ResultsForm

    @method_decorator(login_required(login_url="login"))
    def get(self, request):

        lucky_draw = LuckyDraw.objects.all()
        return render(request,self.result_templet,{"lucky_draw":lucky_draw})

    @method_decorator(login_required(login_url="login"))
    def post(self, request):

        form = self.form_class(request.POST)
        lucky_draw = LuckyDraw.objects.all()
        print("request hit")
        # validate form
        if not form.is_valid():
            return render(request,self.result_templet, {"lucky_draw":lucky_draw,"error":"invalied date"})
     
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
                



# user based reports
class UserReport(View):

    form_class = UserReportForm
    templet = "user_report.html"

    @method_decorator(login_required(login_url="login"))
    def post(self, request):
        """
        this mehod filter participants based on the given form data
        return filtered data(coupens of a perticular user)
        """

        # fetching data and validating
        form = self.form_class(request.POST)
        lucydraw = LuckyDraw.objects.all()
        if not form.is_valid():
            print("invalied form")
            return render(request,self.templet,{"error":"Invalied data","lucydraw":lucydraw})
        
        luckydrawtype_id = form.cleaned_data.get("luckydrawtype_id")
        name = form.cleaned_data.get("name")
        from_date = form.cleaned_data.get("from_date")
        to_date = form.cleaned_data.get("to_date")


        # filter
        if form.cleaned_data.get("luckydrawtype_id") == "ALL":
            filtered_data = Participants.objects.filter(context_id__context_date__range=[from_date,to_date], participant_name__iexact=name)
        else:
            filtered_data = Participants.objects.filter(context_id__context_date__range=[from_date,to_date], participant_name__iexact=name, context_id__luckydrawtype_id = luckydrawtype_id)
        
        lucky_obj = LuckyDraw.objects.get(luckydrawtype_id=luckydrawtype_id)

        return render(request,self.templet,{"filtered_data":filtered_data, "lucydraw":lucydraw, "from_date":from_date, "to_date":to_date, "luckydrawtype_id":luckydrawtype_id,"lucky_obj":lucky_obj,"name":name})
        

    @method_decorator(login_required(login_url="login"))
    def get(self,request):
        
        lucydraw = LuckyDraw.objects.all()
        return render(request, self.templet,{"lucydraw":lucydraw})
    

# additional bitting views
class AdditionalBillingReport(View):

    templet = "billing_user_report.html"
    form_class = AdditionalBillingReportForm
    
    @method_decorator(login_required(login_url="login"))
    def post(self,request):
        """
        this method filter from addition billing port only of a perticular user
        which is given by user and return the result
        """
        
        # fetch data and validate it
        form = self.form_class(request.POST)
        lucydraw = LuckyDraw.objects.exclude(luckydrawtype_id=5)
        if not form.is_valid():
            print("invalied form")
            return render(request,self.templet,{"error":"Invalied data","lucydraw":lucydraw})
            
        # if form is validated, fetch cleaned data from form
        name = form.cleaned_data.get("name")
        luckydrawtype_id = form.cleaned_data.get("luckydrawtype_id")
        billing_date = form.cleaned_data.get("billing_date")

        # filter data from participant table by name matching, and from extra billing port only
        # this is filtering data from only extra billing ports, which id is 5 is hard corder
        # WARNING: filtering from extra billing ports is HARD CODED, problom may occure when extra billing pots id is chnged

        # get today date, we need only data from todays contest
        time_zone = pytz.timezone('Asia/Kolkata')
        date_now = datetime.now(time_zone).date()

        filtered_data = Participants.objects.filter(participant_name__iexact=name,context_id__luckydrawtype_id=5, context_id__context_date=date_now)

        # return response
        lucky_obj = LuckyDraw.objects.get(luckydrawtype_id=luckydrawtype_id)

        return render(request,self.templet,{"filtered_data":filtered_data, "lucydraw":lucydraw,"luckydrawtype_id":luckydrawtype_id,"lucky_obj":lucky_obj,"name":name})

    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        """
        this is returning the additional billing page
        """
        
        lucydraw = LuckyDraw.objects.exclude(luckydrawtype_id=5)
        return render(request, self.templet,{"lucydraw":lucydraw})







"""--------------------  PDF GENERATON VIEWS  ----------------------"""

# Download user report pdf
class UserReportPdf(View):

    form_class = UserReportForm

    @method_decorator(login_required(login_url="login"))
    def post(self, request):

        # fetching data and validating
        form = self.form_class(request.POST)
        if not form.is_valid():
            print("invalied forrm")
            return JsonResponse({"status":401})
        
        # fetching elements from form
        luckydrawtype_id = form.cleaned_data.get("luckydrawtype_id")
        name = form.cleaned_data.get("name")
        from_date = form.cleaned_data.get("from_date")
        to_date = form.cleaned_data.get("to_date")
        
        # filter
        if form.cleaned_data.get("luckydrawtype_id") == "ALL":
            filtered_data = Participants.objects.filter(context_id__context_date__range=[from_date,to_date], participant_name__iexact=name)

            # if user need all data set lucky_draw data to all lucky draw and all time to show in pdf
            luckydraw_data = ["ALL","ALL TIME"]

        else:
            filtered_data = Participants.objects.filter(context_id__context_date__range=[from_date,to_date], participant_name__iexact=name, context_id__luckydrawtype_id = luckydrawtype_id)
            
            # fetch luckydraw_instance and fetch data such as lucky drow name and time to show in pdf
            luckydraw_instance = LuckyDraw.objects.get(luckydrawtype_id=luckydrawtype_id)
            luckydraw_data = [luckydraw_instance.luckydraw_name,luckydraw_instance.draw_time.strftime("%I:%M %p")]

        # createa array of coupem number, count and prize of of winners
        pdf_data = [[i.coupen_number,i.coupen_count,i.prize_rate * i.coupen_count] for i in filtered_data if i.is_winner]
        
        # calculating total winnign prizes
        # got through the pdf_data and last value of the sublist is the total prize of each coupen
        total_winning_prize = 0
        for i in pdf_data:
            total_winning_prize += i[2]

        # this fuctin returns a dict of coupen_type as key and sum as value of passes query set
        coupen_type_wise_rate_sum = coupen_type_rate(query_set=filtered_data)
        
        # create a account dict using generated data and pass to generate_pdf func to show in pdf
        accounts_dict = {}
        accounts_dict.update(coupen_type_wise_rate_sum)
        accounts_dict["total_winning_prize"] = total_winning_prize
        accounts_dict["account_balance"] = total_winning_prize - coupen_type_wise_rate_sum["total_sum"]

        # creating pdf
        date_range = [from_date,to_date]
        data = {
            "name":name,
            "pdf_data":pdf_data,
            "accounts_dict":accounts_dict,
            "date_range":date_range,
            "luckydraw_data":luckydraw_data
        }

        html_location = os.path.join(settings.BASE_DIR,"templates",f"invoice_user.html")
        pdf_save_location = os.path.join(settings.BASE_DIR,"media","user_reports",f"user_report_{name}.pdf")
        
        try:
            generate_pdf_from_html(html_location, pdf_save_location, data)
        except Exception as e:
            print(e)
        
        return JsonResponse({"pdf_url": f'{settings.MEDIA_URL}user_reports/user_report_{name}.pdf'})
        
        
        


# winner announcement report
class WinnerAnnouncementPdf(View):

    form_class = WinnerAnnouncementPdfForm
    pdf_generator_class = generate_winner_pdf

    @method_decorator(login_required(login_url="login"))
    def post(self, request):
        """
        this method accepting a date range
        and returs winners prize list in between the date range
        """
        
        # validate form and fetch cleaned data
        form = self.form_class(request.POST)
        if not form.is_valid():
            return FileResponse()
        
        luckydrawtype_id = form.cleaned_data.get("luckydrawtype_id")
        context_date = form.cleaned_data.get("context_date")

        # getting wontext instance by given data 
        context_instance = LuckyDrawContext.objects.get(luckydrawtype_id = luckydrawtype_id, context_date=context_date)
        
        # fiter participants who is winners
        all_participants = Participants.objects.filter(context_id=context_instance, is_winner=True)

        # seperating winners in to box , block, super reduced format(simpler) to show in pdf
        first_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="FIRST_PRIZE"]
        second_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="SECOND_PRIZE"]
        third_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="THIRD_PRIZE"]
        fourth_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="FOURTH_PRIZE"]
        fifth_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="FIFTH_PRIZE"]
        complimentery_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="COMPLIMENTERY_PRIZE"]

        reduced_winners = first_prize_winners + second_prize_winners + third_prize_winners + fourth_prize_winners + fifth_prize_winners + complimentery_prize_winners

        # generate pdf
        pdf_buffer = generate_winner_pdf(reduced_winners, context_instance)
        
        return FileResponse(pdf_buffer,as_attachment=True, filename="winner_report.pdf")



class ResultFilterPdf(View):

    form_class = ResultsForm

    # @method_decorator(login_required(login_url="login"))
    def post(self, request):

        form = self.form_class(request.POST)
        
        # validate form
        if not form.is_valid():
            print("form not valied")
            print(form.errors)
            return JsonResponse({"status":401})

        # fetch cleaned data
        from_date=form.cleaned_data.get("from_date")
        to_date = form.cleaned_data.get("to_date")
        lucky_drawtype_id=form.cleaned_data.get("lucky_drawtype_id")

        # filter all winner participans data
        if lucky_drawtype_id == "ALL":
            all_participants = Participants.objects.filter(context_id__context_date__range=[from_date,to_date],is_winner=True)

            # if user need all data, lucky draw data set to all to shown in pdf
            lucky_draw_data = ["ALL DRAW", "ALL TIME"]
        
        else:
            all_participants = Participants.objects.filter(context_id__context_date__range=[from_date,to_date],context_id__luckydrawtype_id = lucky_drawtype_id, is_winner=True)

            luckydraw_instance = LuckyDraw.objects.get(luckydrawtype_id = lucky_drawtype_id)
            lucky_draw_data = [luckydraw_instance.luckydraw_name, luckydraw_instance.draw_time.strftime("%I:%M %p")]

        # seperating winners in to box , block, super reduced format(simpler) to show in pdf
        first_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="FIRST_PRIZE"]
        second_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="SECOND_PRIZE"]
        third_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="THIRD_PRIZE"]
        fourth_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="FOURTH_PRIZE"]
        fifth_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="FIFTH_PRIZE"]
        complimentery_prize_winners = [[i.coupen_number,i.prize, i.coupen_count, i.coupen_count * i.prize_rate] for i in all_participants if i.prize=="COMPLIMENTERY_PRIZE"]

        reduced_winners_list = first_prize_winners + second_prize_winners + third_prize_winners + fourth_prize_winners + fifth_prize_winners + complimentery_prize_winners

        # filter data by date using DateFilter class instance
        date_filter = DateFilter(
            from_date=form.cleaned_data.get("from_date"),
            to_date = form.cleaned_data.get("to_date"),
            lucky_drawtype_id=form.cleaned_data.get("lucky_drawtype_id"),
        )

        # get account detains in the selected time period
        accounts = date_filter.get_accounts()

        # prepare table content
        # TABLE 1  coupen type, count, amount and sum it
        # this table shows in the top of the pdf, this format is directly inject to the pdf
        count_table = [
            ["BOX",accounts.get("box_count"),accounts.get("box_total_value")],
            ["BLOCK",accounts.get("block_count"),accounts.get("block_total_value")],
            ["SUPER",accounts.get("super_count"),accounts.get("super_total_value")],
            ["","Total Coupen amount",accounts.get("total_value")]
        ]

        prize_table = [
            ["First prize total",accounts.get("first_prize_total")],
            ["Second prize totat",accounts.get("second_prize_total")],
            ["Third prize total",accounts.get("third_prize_total")],
            ["Fourth prize total",accounts.get("fourth_prize_total")],
            ["Fifth prize total",accounts.get("fifth_prize_total")],
            ["Complimentary prize total",accounts.get("complimentary_prize_total")],
            ["Total Prize amount",accounts.get("total_prize")]
        ]

        # generate and save pdf to media files
        data = {
            "count_table" : count_table,
            "prize_table" : prize_table,
            "reduced_winners_list" : reduced_winners_list,
            "profit" : accounts["profit"],
            "date_range" : [from_date,to_date],
            "lucky_draw_data" : lucky_draw_data
        }

        html_location = os.path.join(settings.BASE_DIR,"templates","report.html")
        pdf_save_location = os.path.join(settings.BASE_DIR,"media","price_report","result_report.pdf")
        try:
            generate_pdf_from_html(html_location, pdf_save_location, data)
        except Exception as e:
            print(e)

        return JsonResponse({"pdf_url": f'{settings.MEDIA_URL}price_report/user_report.pdf'})
    

# additional billing pdf
class AdditionalBillingPdf(View):

    form_class = AdditionalBillingReportPdfForm

    @method_decorator(login_required(login_url="login"))
    def post(self, request):
        """
        this method fetch additional billing info such as for which port and date
        then filter participants by name and creates pdf and returns
        """

        # fetching data and validating
        form = self.form_class(request.POST)
        if not form.is_valid():
            print("invalied forrm")
            return JsonResponse({"status":401})
        
        # fetching elements from form
        luckydrawtype_id = form.cleaned_data.get("luckydrawtype_id")
        name = form.cleaned_data.get("name")
        billing_date = form.cleaned_data.get("billing_date")
        
        # filter data from participant table by name matching, and from extra billing port only
        # this is filtering data from only extra billing ports, which id is 5 is hard corder
        # WARNING: filtering from extra billing ports is HARD CODED, problom may occure when extra billing pots id is chnged

        # get today date, we need only data from todays contest
        time_zone = pytz.timezone('Asia/Kolkata')
        date_now = datetime.now(time_zone).date()
        
        # filter
        filtered_data = Participants.objects.filter(participant_name__iexact=name,context_id__luckydrawtype_id=5, context_id__context_date=date_now)
        
        # fetch luckydraw_instance and fetch data such as lucky drow name and time to show in pdf
        luckydraw_instance = LuckyDraw.objects.get(luckydrawtype_id=luckydrawtype_id)
        luckydraw_data = [luckydraw_instance.luckydraw_name,luckydraw_instance.draw_time.strftime("%I:%M %p")]
        
        pdf_data = [[i.coupen_number,i.coupen_count,i.prize_rate * i.coupen_count] for i in filtered_data if i.is_winner]
        
        # calculating total winnign prizes
        # got through the pdf_data and last value of the sublist is the total prize of each coupen
        total_winning_prize = 0
        for i in pdf_data:
            total_winning_prize += i[2]

        # this fuctin returns a dict of coupen_type as key and sum as value of passes query set
        coupen_type_wise_rate_sum = coupen_type_rate(query_set=filtered_data)
        
        # create a account dict using generated data and pass to generate_pdf func to show in pdf
        accounts_dict = {}
        accounts_dict.update(coupen_type_wise_rate_sum)
        accounts_dict["total_winning_prize"] = total_winning_prize
        accounts_dict["account_balance"] = total_winning_prize - coupen_type_wise_rate_sum["total_sum"]

        # creating pdf
        date_range = [billing_date,billing_date]
        data = {
            "name":name,
            "pdf_data":pdf_data,
            "accounts_dict":accounts_dict,
            "date_range":date_range,
            "luckydraw_data":luckydraw_data
        }
        html_location = os.path.join(settings.BASE_DIR,"templates",f"invoice_user.html")
        pdf_save_location = os.path.join(settings.BASE_DIR,"media","additional_bills",f"additional_bill_{name}.pdf")
        
        try:
            generate_pdf_from_html(html_location, pdf_save_location, data)
        except Exception as e:
            print(e)

        # after prepared the pdf, we have to delete all of the records in the perticular name
        # WARNING : this is not a effective solution, the feature is developed only for a short time period, until developing main feature
        # WANRING : all the records in the extrabilling port of the perticular user is permanantly removed from data base
        # get today date, we need only data from todays contest
        time_zone = pytz.timezone('Asia/Kolkata')
        date_now = datetime.now(time_zone).date()
        
        # filter
        filtered_data = Participants.objects.filter(participant_name__iexact=name,context_id__luckydrawtype_id=5, context_id__context_date=date_now)
        
        # WARNING: deleting permanantly
        filtered_data.delete()

        return JsonResponse({"pdf_url": f'{settings.MEDIA_URL}additional_bills/additional_bill_{name}.pdf'})

