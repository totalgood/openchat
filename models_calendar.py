from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Event(models.Model):
    '''
    This model represents an one-time event
    '''
    title = models.CharField(max_length=255)
    description = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField(
        blank=True,
        # validators=[validate_after]
    )
    #TODO in view, make logic that end time must be later than start time.
    location = models.CharField(max_length=100)
    creator = models.ForeignKey(User, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.end:
            self.end = self.start + timezone.timedelta(hours=1)
        super(Event, self).save(*args, **kwargs)
        if self.end - self.start < timezone.timedelta(0):
            raise ValidationError('end time must occur after start time, is now occuring {} before'.format(self.end - self.start))

    def __str__(self):
        return self.title

