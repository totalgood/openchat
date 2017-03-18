from django.contrib import admin

from twote.models import User, Place, Tweet

admin.site.register(Place)


class TweetAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('text',)
        }),
        ('User', {
            'fields': ('user', 'place')
        }),
        ('Date', {
            'fields': ('created_at', 'created_date', 'modified_date',)
        }),
    )
    date_hierarchy = 'created_date'
    list_display = ('id_str', 'user', 'created_at', 'created_date', 'favorite_count', 'text')
    select_related = True
    search_fields = ['text', 'source', 'tags', 'location',
                     'user__screen_name',
                     'place__place_type', 'place__country_code', 'place__name', 'place__country', 'place__url',
                     ]

    def get_readonly_fields(self, request, obj=None):
        '''Override to make certain fields readonly if this is a change request'''
        if obj is not None:
            # auto_now and auto_now_add fields must are editable=False so must be listed as readonly_fields
            return tuple(list(self.readonly_fields) + ['user', 'place', 'created_at', 'created_date', 'modified_date'])
        return self.readonly_fields


class UserAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_display = 'id id_str screen_name created_date location followers_count statuses_count favourites_count friends_count'.split()

admin.site.register(Tweet, TweetAdmin)
admin.site.register(User, UserAdmin)
