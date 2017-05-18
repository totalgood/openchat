from django.contrib import admin
import pytz

from openspaces import models 

def convert_tz(time_obj):
    """Helper func to convert a models' field times to local TZ"""

    if time_obj:
        fmt = '%H:%M:%S %Z'
        dt = pytz.utc.localize(time_obj)
        out = dt.astimezone(pytz.timezone('US/Pacific'))
        return out.strftime(fmt)
    else:
        # time object is null
        return


class TweetAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Tweet', {
            'fields': ('text',)
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Date', {
            'fields': ('created_at', 'modified_at',)
        }),
    )
    date_hierarchy = 'created_at'
    list_display = ('text', 'user', 'created_at', 'id_str')
    select_related = True
    search_fields = ['text', 'user__screen_name',]

    def get_readonly_fields(self, request, obj=None):
        '''Override to make certain fields readonly if this is a change request'''
        if obj is not None:
            # auto_now and auto_now_add fields must are editable=False so must be listed as readonly_fields
            return tuple(list(self.readonly_fields) + ['user', 'created_at', 'modified_at', 'text'])
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
            return tuple(list(self.readonly_fields) + ['screen_name', 'created_at', 'id_str'])
        return self.readonly_fields


class OutgoingConfigAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['auto_send', 'default_send_interval', 'ignore_users']


class OutgoiningTweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['original_tweet', 'screen_name', 'approved', 
                    'scheduled_outgoing', 'time_sent']

    # methods below needed so admin can call for each object and convert
    def scheduled_outgoing(self, event):
        """convert scheduled_time model field to local TZ"""
        return convert_tz(event.scheduled_time)

    def time_sent(self, event):
        """convert sent_time model field to local TZ"""
        return convert_tz(event.sent_time)


class OpenspacesEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['start_time', 'location', 'creator', 'description']

    def start_time(self, event):
        """convert start model field to local TZ"""
        return convert_tz(event.start)


admin.site.register(models.StreamedTweet, TweetAdmin)
admin.site.register(models.User, TweetUserAdmin)
admin.site.register(models.OutgoingConfig, OutgoingConfigAdmin)
admin.site.register(models.OutgoingTweet, OutgoiningTweetAdmin)
admin.site.register(models.OpenspacesEvent, OpenspacesEventAdmin)
