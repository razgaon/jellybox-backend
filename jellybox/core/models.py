from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    # Inputs:
    #         * name (str): name of task
    #         * priority (int): number from 1 (lowest) to 5 (highest) indicating priority level of task
    #         * duration (int): estimated time to complete task in minutes
    #         * difficulty (int): number from 1 (lowest) to 5 (highest) indicating difficulty of task
    #         * start_date (datetime obj): first day on which task can be completed
    #         * due_date (datetime obj): last day on which task can be completed

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(null=False)
    priority = models.IntegerField(null=False)
    duration = models.IntegerField(default=0, null=True)
    difficulty = models.IntegerField(default=0, null=True)
    start_date = models.DateTimeField(default=None, null=True)
    end_date = models.DateTimeField(default=None, null=True)
    date_added = models.DateTimeField(auto_now=True, null=False)


class Event(models.Model):
    """
    Stores the mappings of task names to actual tasks
    """
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(null=False)
    priority = models.IntegerField(null=False)
    duration = models.IntegerField(default=0, null=True)
    difficulty = models.IntegerField(default=0, null=True)
    start_time = models.DateTimeField(default=None, null=False)
    end_time = models.DateTimeField(default=None, null=False)
    all_day = models.BooleanField(default=False, null=False)
    date = models.DateField(null=False)
    timestamp_added = models.DateTimeField(auto_now=True, null=False)


class UserPreference(models.Model):
    """
            * energy_preferences (list): energy preferences for early morning, late morning, afternoon, early evening, late evening, and night
        * sleep_start (datetime obj): the starting time for sleep
        * sleep_end (datetime obj): the ending time for sleep
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    sleep_start = models.DateTimeField(default=None, null=False)
    sleep_end = models.DateTimeField(default=None, null=False)
    energy_levels = models.TextField(null=False)


