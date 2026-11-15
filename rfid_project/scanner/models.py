from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone

class NoDeleteQuerySet(models.QuerySet):
    def delete(self):
        raise PermissionDenied("User records are permanent and cannot be deleted")

class User(models.Model):
    full_name = models.CharField(max_length=100)
    address = models.TextField(help_text='Enter your address here')

    objects = NoDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        raise PermissionDenied("User records are permanent and cannot be deleted")

    def __str__(self):
        return f'{self.full_name}'

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
    supplies_received = models.TextField()
    location = models.CharField(max_length=150)

    objects = NoDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        raise PermissionDenied("User records are permanent and cannot be deleted")

    def __str__(self):
        return f'{self.card_scanned} {self.timestamp} {self.supplies_received} {self.location}'

class AdminSetReliefLog(models.Model):
    location = models.CharField(max_length=150)
    supplies_relief = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    objects = NoDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Records are permanent and cannot be deleted")

    def __str__(self):
        return f'{self.location} {self.supplies_relief}'