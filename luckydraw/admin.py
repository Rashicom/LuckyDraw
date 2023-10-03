from django.contrib import admin
from .models import LuckyDraw,LuckyDrawContext,Participants


# Register your models here.
admin.site.register(LuckyDraw)
admin.site.register(LuckyDrawContext)
admin.site.register(Participants)
