from django.db import models

class AttendanceLog(models.Model):
    uid = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uid} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"