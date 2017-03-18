import django_filters
from twote.models import OutgoingTweet

APPROVAL_CHOICES = (
    (0, 'needs_action'),
    (1, 'Approved'),
    (2, 'Denied'),
)

class OutgoingTweetFilter(django_filters.FilterSet):
    approved = django_filters.ChoiceFilter(choices=APPROVAL_CHOICES)

    class Meta:
        model = OutgoingTweet
        fields = ['approved',]