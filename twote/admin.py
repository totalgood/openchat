from django.contrib import admin
import pytz

from twote import models 


class TweetAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Tweet', {
            'fields': ('text',)
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Date', {
            'fields': ('created_at', 'modified_date',)
        }),
    )
    date_hierarchy = 'created_at'
    list_display = ('text', 'user', 'created_at')
    select_related = True
    search_fields = ['text', 'user__screen_name',]

    def get_readonly_fields(self, request, obj=None):
        '''Override to make certain fields readonly if this is a change request'''
        if obj is not None:
            # auto_now and auto_now_add fields must are editable=False so must be listed as readonly_fields
            return tuple(list(self.readonly_fields) + ['user', 'created_at', 'modified_date'])
        return self.readonly_fields


class TweetUserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Twitter User', {
            'fields': ('screen_name', 'id_str', 'should_ignore')
        }),
    )
    date_hierarchy = 'created_at'
    list_display = ['screen_name', 'id_str', 'should_ignore']
    search_fields = ['screen_name']

    def get_readonly_fields(self, request, obj=None):
        '''Override to make certain fields readonly if this is a change request'''
        if obj is not None:
            # auto_now and auto_now_add fields must are editable=False so must be listed as readonly_fields
            return tuple(list(self.readonly_fields) + ['screen_name', 'created_date', 'id_str'])
        return self.readonly_fields


class OutgoingConfigAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['auto_send', 'default_send_interval', 'ignore_users']


class OutgoiningTweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'scheduled_time'
    list_display = ['original_tweet', 'screen_name', 'approved', 
                    'scheduled_time_in_timezone', 'sent_time']

    # list_display = [..., 'event_datetime_in_timezone', ...]

    def scheduled_time_in_timezone(self, event):
        """Display each event time on the changelist in its own timezone"""
        fmt = '%Y-%m-%d %H:%M:%S %Z'
        dt = pytz.utc.localize(event.scheduled_time).astimezone(pytz.timezone('US/Pacific'))
        return dt.strftime(fmt)
    scheduled_time_in_timezone.short_description = ('Scheduled Time')


class OpenspacesEventAdmin(admin.ModelAdmin):
    list_display = ['start', 'location', 'creator', 'description']


admin.site.register(models.StreamedTweet, TweetAdmin)
admin.site.register(models.User, TweetUserAdmin)
admin.site.register(models.OutgoingConfig, OutgoingConfigAdmin)
admin.site.register(models.OutgoingTweet, OutgoiningTweetAdmin)
admin.site.register(models.OpenspacesEvent, OpenspacesEventAdmin)
