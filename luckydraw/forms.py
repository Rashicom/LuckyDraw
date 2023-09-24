from django import forms
from .models import LuckyDraw

class AddParticipantForm(forms.Form):
    luckydrawtype_id = forms.IntegerField(required=True)
    participant_name = forms.CharField(required=False)
    coupen_number = forms.CharField(required=True)
    coupen_type = forms.CharField(required=True)
    coupen_count = forms.IntegerField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        coupen_count = cleaned_data.get('coupen_count')

        if coupen_count is not None and coupen_count <= 0:
            self.add_error(None,"invalied coupen count")

        return cleaned_data


class GetorSetLuckyDrawForm(forms.ModelForm):
    class Meta:
        model = LuckyDraw
        fields = ['luckydraw_name','description','draw_time']

