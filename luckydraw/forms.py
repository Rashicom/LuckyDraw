from django import forms


class AddParticipantForm(forms.Form):
    luckydrawtype_id = forms.IntegerField(required=True)
    participant_name = forms.CharField(required=False)
    coupen_number = forms.CharField(required=True)
    coupen_type = forms.CharField(required=True)
    coupen_count = forms.IntegerField(required=True)
