from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Sum
from .serializers import ActivitySerializer, GoalSettingSerializer
from .models import Activity, Goal
from notifications.models import Notification


# Create your views here.


class ListCreateActivityView(generics.ListCreateAPIView):
    """
    Extending ListCreateApiView to have the Get/Post options
    IsAuthenticated to only allow authenticated users to view or create the activity
    DjangoFilterBackend and Orderfilter to allow Filtering based on activity_type and date by using ?activity_type=
    or ?ordering=distance duration or calories_burned
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = {'activity_type': ['exact', 'icontains'],
                        'date__date': ['gte', 'lte']
                        }
    ordering_fields = ['distance', 'duration', 'calories_burned']

    def get_queryset(self):
        """
        overriding this to only filter the Activity based on the logged in user and ordering it by the date it was created
        to show newer activities first
        """
        user = self.request.user
        return Activity.objects.filter(user=user).order_by('-date')

    def perform_create(self, serializer):
        """
        Overriding the create method for 2 reasons
        1- Automatically assign the activity to the logged in user using Serializer.save(user=self.request.user)
        2- creating a Notification upon creating the activity with a custom distance_text that shows the distance if any
        """
        activity = serializer.save(user=self.request.user)

        distance_text = f"Distance: {activity.distance} km" if activity.distance is not None else ""

        Notification.objects.create(
            recipient=self.request.user,
            verb=f"You have created a new Activity: {activity.activity_type}, Duration: {activity.duration} minutes, "
                 f"{distance_text}, Calories: {activity.calories_burned} kcal"
        )


class DetailActivityView(generics.RetrieveUpdateDestroyAPIView):
    """
    Extending RetrieveUpdateDestroyApiView  to allow for GET/PUT/PATCH/DELETE methods for a single activity by adding
    /<int:pk> to the url
    IsAuthenticated method to allow only logged in users
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        overridng the get_queryset to return the activity of the logged in user
        """
        user = self.request.user
        return Activity.objects.filter(user=user)

    def perform_update(self, serializer):
        """
        overriding the update method to create a Notification upon updating an Activity
        """
        activity = serializer.save()

        distance_text = f"Distance: {activity.distance} km" if activity.distance is not None else ""
        Notification.objects.create(
            recipient=self.request.user,
            verb=f"You have updated an Activity: {activity.activity_type}, Duration: {activity.duration} minutes, "
                 f"{distance_text}, Calories: {activity.calories_burned} kcal"
        )

    def perform_destroy(self, instance):
        """
        overriding the destroy method to send a notification upon deleting an activity
        return the super().perform_destroy(instance) because in update the serializer.save() takes care of automatically
        saving the update
        but in destroy i have to return super to actually delete the activity after sending the notification
        """
        activity = instance

        distance_text = f"Distance: {activity.distance} km" if activity.distance is not None else ""
        Notification.objects.create(
            recipient=self.request.user,
            verb=f"You have Deleted an Activity: {activity.activity_type}, Duration: {activity.duration} minutes, "
                 f"{distance_text}, Calories: {activity.calories_burned} kcal"
        )

        super().perform_destroy(instance)


class ListCreateGoalView(generics.ListCreateAPIView):
    """
    Extending ListCreateApiView to have the Get/Post options
    IsAuthenticated to only allow authenticated users to view or create the activity
    """
    serializer_class = GoalSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Overriding the create method for 2 reasons
        1- Automatically assign the goal to the logged in user using Serializer.save(user=self.request.user)
        2- creating a Notification upon creating the goal
        """
        goal = serializer.save(user=self.request.user)

        Notification.objects.create(
            recipient=self.request.user,
            verb=f"New Goal Created {goal.activity_type} -Target: {goal.target} {goal.goal_type}")

    def get_queryset(self):
        """
       overriding this to only filter the Activity based on the logged in user and ordering it by the date it was created
       to show newer activities first
        """
        return Goal.objects.filter(user=self.request.user)


class DetailGoalView(generics.RetrieveUpdateDestroyAPIView):
    """
    Extending RetrieveUpdateDestroyApiView  to allow for GET/PUT/PATCH/DELETE methods for a single goal by adding
    /<int:pk> to the url
    IsAuthenticated method to allow only logged in users
    """
    serializer_class = GoalSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        overriding the get_queryset to return the goal of the logged in user
        """
        return Goal.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        goal = serializer.save()
        Notification.objects.create(
            recipient=self.request.user,
            verb=f"Goal updated: {goal.activity_type} -, New Target: {goal.target} {goal.goal_type}!"
        )

    def perform_destroy(self, instance):
        """
        overriding the destroy method to send a notification upon deleting a goal
        return the super().perform_destroy(instance) because in update the serializer.save() takes care of automatically
        saving the update
        but in destroy i have to return super to actually delete the goal after sending the notification
        """
        goal = instance
        Notification.objects.create(
            recipient=self.request.user,
            verb=f"Goal Deleted: {goal.activity_type}"
        )

        super().perform_destroy(instance)


class ActivityTotalsView(generics.GenericAPIView):
    """
    a View to show the total activity and goals for a specific user
    we start by getting the user from request.user
    today from timezone.today
    and the period from the url by using query_params.get either we get the period if defined or default to all
    then we have an if condition to get the activities of that certain period either all, week or a month
    we make a dictionary using aggregate method and Sum the calories_burned,distance and duration
    then we get the goals that was set by logged in user and make an empty list
    we loop over the goals, and we filter by the activity_type
    we get the current progress of the goal_type that was chosen by using aggregate
    total=Sum('distance') will create a dict {total:distance} then we choose that number ['total'] or 0 so it doesn't
    return None
    and getting the remaining progress using max 0 or the remaining number so its never a negative number
    everytime i hit the endpoint all notifications will be regenerated so i have to check first if the notification exists
    using .exists() if not we create it
    and we append all the goals to the list so i can return it in the Response with the total activities of that user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.now()
        period = self.request.query_params.get('period', 'all')

        if period == 'all':
            activities = Activity.objects.filter(user=user)
        elif period == 'week':
            start_date = today - timezone.timedelta(days=7)
            activities = Activity.objects.filter(user=user, date__gte=start_date)
        elif period == 'month':
            start_date = today - timezone.timedelta(days=30)
            activities = Activity.objects.filter(user=user, date__gte=start_date)

        else:
            return Response({"error": "Invalid Period"}, status=status.HTTP_400_BAD_REQUEST)

        totals = activities.aggregate(
            total_calories=Sum('calories_burned'),
            total_distance=Sum('distance'),
            total_duration=Sum('duration')
        )

        goals = Goal.objects.filter(user=user)
        goals_data = []

        for goal in goals:
            goal_activities = activities.filter(activity_type=goal.activity_type)

            if goal.goal_type == 'distance':
                current_progress = goal_activities.aggregate(total=Sum('distance'))['total'] or 0
            if goal.goal_type == 'duration':
                current_progress = goal_activities.aggregate(total=Sum('duration'))['total'] or 0
            else:
                current_progress = goal_activities.aggregate(total=Sum('calories_burned'))['total'] or 0

            remaining = max(0, goal.target - current_progress)

            if remaining <= 0:
                notifications_exist = Notification.objects.filter(
                    recipient=user,
                    verb=f"You have Reached your goal: {goal.activity_type} - {goal.goal_type}!"
                ).exists()

                if not notifications_exist:
                    Notification.objects.create(
                        recipient=user,
                        verb=f"You have Reached your goal: {goal.activity_type} - {goal.goal_type}!",
                    )

            goals_data.append({
                "goal_type": goal.goal_type,
                "time_period": goal.time_period,
                "activity_type": goal.activity_type,
                "target": goal.target,
                "current_progress": current_progress,
                "remaining": remaining
            })

        return Response({
            "period": period,
            'start_date': start_date.date() if period != 'all' else "All",
            'total_calories_burned': totals['total_calories'] or 0,
            'total_distance': totals['total_distance'] or 0,
            'total_duration': totals['total_duration'] or 0,
            "goals": goals_data
        })


class LeaderboardView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Getting the period from the url or setting it to all if not provided , raising an error if something else beside
        all,week,month is provided
        we then get all activities in that timezone specified
        we use actitivies.values(user__username) which will return a dicitionary with all users's username
        then we use annotate to Sum Calories,distnace and duration for each user and we order it from highest to lowest
        and return only the top 3

         Methods:
        - `values('user__username')`: Groups the activities by the username of the user.
        - `annotate(Sum())`: Calculates the sum of calories, distance, and duration for each group of activities.
        - `order_by()`: Sorts the leaderboard in descending order based on the aggregated value.
        """
        period = self.request.query_params.get('period', 'all')
        today = timezone.now()

        if period == 'all':
            activities = Activity.objects.all()
        elif period == 'week':
            start_date = today - timezone.timedelta(days=7)
            activities = Activity.objects.filter(date__gte=start_date)
        elif period == 'month':
            start_date = today - timezone.timedelta(days=30)
            activities = Activity.objects.filter(date__gte=start_date)
        else:
            return Response({"error": "Invalid Period"}, status=status.HTTP_400_BAD_REQUEST)

        calories_leaderboard = activities.values('user__username').annotate(
            total_calories=Sum('calories_burned')
        ).order_by('-total_calories')[:3]

        distance_leaderboard = activities.values('user__username').annotate(
            total_distance=Sum('distance')
        ).order_by('-total_distance')[:3]

        duration_leaderboard = activities.values('user__username').annotate(
            total_duration=Sum('duration')
        ).order_by('-total_duration')[:3]

        return Response({
            "period": period,
            "calories_leaderboard": list(calories_leaderboard),
            "distance_leaderboard": list(distance_leaderboard),
            "duration_leaderboard": list(duration_leaderboard)
        })
