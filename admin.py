from django.contrib import admin

from twote.models import User, Place, Tweet

admin.site.register(User)
admin.site.register(Place)
admin.site.register(Tweet)
