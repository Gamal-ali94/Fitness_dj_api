from django.urls import path
from .views import (ListCreateActivityView, DetailActivityView, ActivityTotalsView,
                    DetailGoalView, ListCreateGoalView, LeaderboardView)

urlpatterns = [
    path('activities/', ListCreateActivityView.as_view(), name='activities'),
    path('activities/<int:pk>/', DetailActivityView.as_view(), name='activity'),
    path('activities/total/', ActivityTotalsView.as_view(), name='activity-total'),
    path('goals/', ListCreateGoalView.as_view(), name='goals'),
    path('goals/<int:pk>/', DetailGoalView.as_view(), name='goal-detail'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),

]
