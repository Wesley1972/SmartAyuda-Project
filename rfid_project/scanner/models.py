from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone

class NoDeleteQuerySet(models.QuerySet):
    def delete(self):
        raise PermissionDenied("User records are permanent and cannot be deleted")

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField(help_text='Enter your address here')

    objects = NoDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        raise PermissionDenied("User records are permanent and cannot be deleted")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class RFIDCard(models.Model):
    uid = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)

    objects = NoDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        raise (PermissionDenied("User records are permanent and cannot be deleted"))

    def __str__(self):
        return f'{self.uid}'

class ReliefLog(models.Model):
    card_scanned = models.ForeignKey(RFIDCard, on_delete=models.PROTECT, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    supplies_received = models.IntegerField()
    location = models.CharField(max_length=150)

    objects = NoDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        raise PermissionDenied("User records are permanent and cannot be deleted")

    def __str__(self):
        return f'{self.card_scanned} {self.timestamp} {self.supplies_received} {self.location}'

