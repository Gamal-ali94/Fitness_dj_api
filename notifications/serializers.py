from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    have recipient as a ReadOnlyField so its not modified during update or create with the source recipient
    username to automatically assign it
    timestamp changing the format to more readable one and read_only to True to not allowing it to change
    """
    recipient = serializers.ReadOnlyField(source='recipient.username')
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p", read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'verb', 'timestamp']
