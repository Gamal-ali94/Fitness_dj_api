from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.

class Activity(models.Model):
    """
    The Activity model tracks user  activities such as running, cycling, or weightlifting.

    Activity  type Choices to limit users to those 3 activities and
    user : one user can have many activities with models.cascade so if i delete the user all related activities are deleted
    duration: a positive integerfield so it can't be a negative number with a help text
    distance floatfield thats optional incase the activity doesn't include distance
    calories_burned another positive intg field
    date with an auto now add to automatically add the date this activity was created
    """
    ACTIVITY_TYPE_CHOICES = [
        ("running", "Running"),
        ("cycling", "Cycling"),
        ("weightlifting", "Weight Lifting")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activties')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    duration = models.PositiveIntegerField(help_text='Duration in minutes')
    distance = models.FloatField(help_text="Distance in kilometers", blank=True, null=True)
    calories_burned = models.PositiveIntegerField(help_text="calories burned")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} on {self.date}"


class Goal(models.Model):
    """
    Goal Model that allow users to set goals choosing the activity_Type and the goal_type and the period they want

    User : Foreign key to allow one user to have multiple goals
    goal_type choice field between distance , duration or calories
    activity_type : choice field between the activity type running, cycling or weight lifting
    target : a float field to allow the user to set the target he wants for his goal ex 1000 calorie etc
    time_period: A CharField that allows the user to define the time frame for the goal
    created_at an auto_now_add datetimefield to automatically set the time this goal was created
    """
    GOAL_TYPE_CHOICES = [
        ("distance", "Distance"),
        ("duration", "Duration"),
        ("calories", "Calories")
    ]
    ACTIVITY_TYPE_CHOICES = [
        ("running", "Running"),
        ("cycling", "Cycling"),
        ("weightlifting", "Weight Lifting")
    ]
    TIME_PERIOD_CHOICES =[
        ('week', 'Week'),
        ('month', 'Month'),
        ('all', 'All Time'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPE_CHOICES)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    target = models.FloatField("your target in numbers")
    time_period = models.CharField(max_length=50, choices=TIME_PERIOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
