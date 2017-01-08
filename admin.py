from django.contrib import admin

from twote.models import User, Place, Tweet

admin.site.register(User)
admin.site.register(Place)


class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_display = ('id_str', 'user__id' 'user__name', 'created_date', 'created_at', 'text')


admin.site.register(Tweet, TweetAdmin)
