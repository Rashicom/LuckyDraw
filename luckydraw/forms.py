from django import forms
from .models import LuckyDraw

class AddParticipantForm(forms.Form):
    luckydrawtype_id = forms.IntegerField(required=True)
    participant_name = forms.CharField(required=False)
    coupen_number = forms.CharField(required=True)
    coupen_type = forms.CharField(required=True)
    count_limit = forms.IntegerField(required=True)

class BulkAddParticipantForm(forms.Form):
    luckydrawtype_id = forms.IntegerField(required=True)
    participant_name = forms.CharField(required=False)
    coupen_file = forms.FileField(required=True)
    count_limit = forms.IntegerField(required=True)
    

class GetorSetLuckyDrawForm(forms.ModelForm):
    class Meta:
        model = LuckyDraw
        fields = ['luckydraw_name','description','draw_time']


class AnnounceWinnerForm(forms.Form):
    lucky_numbers = forms.CharField(required=True)
    luckydrawtype_id = forms.IntegerField(required=True)
    context_date = forms.DateField(required=True)
    

class ResultsForm(forms.Form):
    lucky_drawtype_id = forms.CharField(required=True)
    from_date = forms.DateField(required=True)
    to_date = forms.DateField(required=True)



# user based report form
class UserReportForm(forms.Form):
    name = forms.CharField(required=True)
    luckydrawtype_id = forms.CharField(required=True)
    from_date = forms.DateField(required=True)
    to_date = forms.DateField(required=True)



class WinnerAnnouncementPdfForm(forms.Form):
    luckydrawtype_id = forms.IntegerField(required=True)
    context_date = forms.DateField(required=True)



# additional billign form
class AdditionalBillingReportForm(forms.Form):
    name = forms.CharField(required=True)
    luckydrawtype_id = forms.CharField(required=False)
    billing_date = forms.DateField(required=False)


# inherit the AdditionalBillingReportForm and set lucky id and date requered status to true
# here we need all informations to generate pdf
class AdditionalBillingReportPdfForm(AdditionalBillingReportForm):
    luckydrawtype_id = forms.CharField(required=True)
    billing_date = forms.DateField(required=True)