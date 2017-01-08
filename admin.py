from django.contrib import admin

from twote.models import User, Place, Tweet

admin.site.register(User)
admin.site.register(Place)


class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'


admin.site.register(Tweet, TweetAdmin)
