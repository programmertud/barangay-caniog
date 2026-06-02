from django.db import models

class ReliefEvent(models.Model):
    STATUS_CHOICES = (
        ('PLANNED', 'Planned'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    EVENT_TYPES = (
        ('FLOOD', 'Flood Relief'),
        ('TYPHOON', 'Typhoon Aid'),
        ('FIRE', 'Fire Victim Support'),
        ('EARTHQUAKE', 'Earthquake Response'),
        ('MEDICAL', 'Medical Outreach'),
        ('OTHER', 'Other Emergency'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PLANNED')
    
    assigned_personnel = models.ManyToManyField('accounts.User', related_name='assigned_events')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
