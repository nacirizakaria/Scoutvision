from django.contrib import admin
from .models import Shortlist, PlayerNote, Profile

# Register your models here.

admin.site.register(Shortlist)
admin.site.register(PlayerNote)
admin.site.register(Profile)
