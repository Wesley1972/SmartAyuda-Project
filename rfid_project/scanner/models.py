from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone

class NoDeleteQuerySet(models.QuerySet):
    def delete(self):
        raise PermissionDenied("User records are permanent and cannot be deleted")

class User(models.Model):
    full_name = models.CharField(max_length=100)
    address = models.TextField(help_text='Enter your address here')
    role = models.CharField(max_length=10, default='user')

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

class AdminSetReliefLog(models.Model):
    users = models.ManyToManyField(User, blank=True)
    location = models.CharField(max_length=150)
    supplies_relief = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    objects = NoDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Records are permanent and cannot be deleted")

    def __str__(self):
        return f'{self.location} {self.supplies_relief}'

class AidClaim(models.Model):
    relief_log = models.ForeignKey(AdminSetReliefLog, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    time_received = models.DateTimeField(default=timezone.now)

    objects = NoDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Records are permanent and cannot be deleted")

