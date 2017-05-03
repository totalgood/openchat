from django.contrib import admin

from twote.models import User, StreamedTweet, OutgoingConfig, OutgoingTweet


class TweetAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Tweet', {
            'fields': ('text',)
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Date', {
            'fields': ('created_date', 'modified_date',)
        }),
    )
    date_hierarchy = 'created_date'
    list_display = ('text', 'user', 'created_date')
    select_related = True
    search_fields = ['text', 'user__screen_name',]

    def get_readonly_fields(self, request, obj=None):
        '''Override to make certain fields readonly if this is a change request'''
        if obj is not None:
            # auto_now and auto_now_add fields must are editable=False so must be listed as readonly_fields
            return tuple(list(self.readonly_fields) + ['user', 'created_date', 'modified_date'])
        return self.readonly_fields


class TweetUserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Twitter User', {
            'fields': ('screen_name', 'id_str')
        }),
    )
    date_hierarchy = 'created_date'
    list_display = ['screen_name', 'id_str']
    search_fields = ['screen_name']

    def get_readonly_fields(self, request, obj=None):
        '''Override to make certain fields readonly if this is a change request'''
        if obj is not None:
            # auto_now and auto_now_add fields must are editable=False so must be listed as readonly_fields
            return tuple(list(self.readonly_fields) + ['screen_name', 'created_date', 'id_str'])
        return self.readonly_fields


class OutgoingConfigAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_display = ['auto_send', 'default_send_interval', 'ignore_users']


class OutgoiningTweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'scheduled_time'
    list_display = ['tweet', 'approved', 'scheduled_time', 'sent_time']


admin.site.register(StreamedTweet, TweetAdmin)
admin.site.register(User, TweetUserAdmin)
admin.site.register(OutgoingConfig, OutgoingConfigAdmin)
admin.site.register(OutgoingTweet, OutgoiningTweetAdmin)
