from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from .models import Activity, Goal


class ActivitySerializer(serializers.ModelSerializer):
    """
    setting user to readonlyfield with the source user.username so it shows the loggedin user username and not allowing
    modifying during updating or creating the serializer
    date read_only set to True to also not allow modifiying and changing the format to a more human readable one
    overriding the validate method :
    first we get the activity_type for the data.get('activity_type')
    we check if activity type is either running or cycling and there's no distance provided , we raise a validation error
    that asks the user to insert a distance during activity creation
    and we return the data
    """
    user = serializers.ReadOnlyField(source='user.username')
    date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p", read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'user', 'activity_type', 'duration', 'distance', 'calories_burned', 'date']

    def validate(self, data):
        activity_type = data.get('activity_type')
        if activity_type in ['running', 'cycling'] and data.get('distance') is None:
            raise serializers.ValidationError({
                'distance': "distance is required for running and cycling activities"
            })
        return data


class GoalSettingSerializer(serializers.ModelSerializer):
    """
    Again with User and created_at readonlyfields and representing the user using source = 'user.username'
    Current_progress and remaining are SerializerMethodField means its not in the model but dynamically created
    when the serializer is created
    """
    user = serializers.ReadOnlyField(source='user.username')
    created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p", read_only=True)
    current_progress = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ['id', 'user', 'activity_type', 'goal_type', 'target', 'time_period', 'current_progress', 'remaining',
                  'created_at']

    def get_current_progress(self, obj):
        """
        this method to calculate the progress towards the goal
        first we get the logged in user using self.context['request'].user , the request here have all the fields data
        i get today's time using timezone.now()
        we filter the time_period by either week month of all data and save it in activities
        then i get the current_progress of either distance,duration or calories_burned and i aggregate it
        aggregate method creates a dictionary of total:Sum(goal_type)
        i use or 0 so i don't get None its either a total number or 0
        and i return the current progress
        """
        user = self.context['request'].user
        today = timezone.now()

        if obj.time_period == 'week':
            start_date = today - timezone.timedelta(days=7)
            activities = Activity.objects.filter(user=user, activity_type=obj.activity_type, date__gte=start_date)

        if obj.time_period == 'month':
            start_date = today - timezone.timedelta(days=30)
            activities = Activity.objects.filter(user=user, activity_type=obj.activity_type, date__gte=start_date)

        else:
            activities = Activity.objects.filter(user=user, activity_type=obj.activity_type)

        if obj.goal_type == 'distance':
            current_progress = activities.aggregate(total=Sum('distance'))['total'] or 0
        elif obj.goal_type == 'duration':
            current_progress = activities.aggregate(total=Sum('duration'))['total'] or 0
        else:
            current_progress = activities.aggregate(total=Sum('calories_burned'))['total'] or 0

        return current_progress

    def get_remaining(self, obj):
        """
        this method to calculate how much left of the goal to achieve
        i use max so the remainin is never a negative number its the bigger number between 0 or obj.target-current_progress
        """
        current_progress = self.get_current_progress(obj)
        return max(0, obj.target - current_progress)
