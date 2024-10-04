from rest_framework import permissions
from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer
# Create your views here.


class NotificationListView(generics.ListAPIView):
    """
    extending ListAPIView because its a list of notifications
    permissions IsAuthenticated so only logged in users can see the notifications
    overriding the get_queryset to filter it based on the logged in user recipient=self.request.user and ordering it by
    timestamp to show notifications from newer to older
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-timestamp')