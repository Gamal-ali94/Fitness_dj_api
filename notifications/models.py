from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

User = get_user_model()


class Notification(models.Model):
    """
    Notifications models to send notifications to users and can be linked to different models like goals or activities
    using Django Content Type Framework
    Fields
    Recipient : the user who will receive the notification
    verb : what's the notification about ( achieving a goal or updating/creating an activity )
    target_content_Type: connects any model to the notification
    target_object_id = stores the id of the model linking notification
    target: a generic foregin key used to link notification to any model together with target_content_Type and
    target_object_id
    timestamp:when the notification was creating and using auto_now_add to automatically add it
    """
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    verb = models.CharField(max_length=150)

    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    target_object_id = models.PositiveIntegerField(blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.verb} - {self.target}"
