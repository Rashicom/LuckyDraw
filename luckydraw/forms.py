from django import forms
from .models import LuckyDraw

class AddParticipantForm(forms.Form):
    luckydrawtype_id = forms.IntegerField(required=True)
    participant_name = forms.CharField(required=False)
    coupen_number = forms.CharField(required=True)
    coupen_type = forms.CharField(required=True)
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
