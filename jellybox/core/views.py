import datetime
from http import HTTPStatus

from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.views import APIView
from preferences import *
from models import *

HOURS_PER_DAY = 24
MINUTES_PER_HOUR = 60
BLOCKS_PER_HOUR = 4
MINUTES_PER_BLOCK = 60
BLOCK_LENGTH = 15


class SetPreference(APIView):
    """
    Returns the current state of the game with the provided game id
    """

    def post(self, request, format=None):
        user_id = request.POST.get("user_id")
        sleep_start_time = request.POST.get("sleep_start_time")
        sleep_end_time = request.POST.get("sleep_end_time")
        energy_levels = request.POST.get("energy_levels")

        data = {'user_id': user_id,
                'sleep_start_time': sleep_start_time,
                'sleep_end_time': sleep_end_time,
                'energy_levels': energy_levels}

        preference = UserPreference(**data)
        preference.save()

        return HttpResponse(status=HTTPStatus.OK)
        # return JsonResponse(data, safe=False)


class GetSchedule(APIView):
    """
    Returns the current state of the game with the provided game id
    """

    def get(self, request, format=None):
        user_id = request.GET.get("game_id")

        today = datetime.date.today()
        week_from_now = today + datetime.timedelta(7)
        preferences = UserPreference.objects.filter(user_id=user_id)
        events = Event.objects.filter(user_id=user_id)
        # Get only until next week
        # Get the events
        schedule = Schedule(today, week_from_now, preferences, events, tasks)

        # Send to user

        # otherwise just query and send
        return Response("")


class CreateSchedule(APIView):
    """
    Returns the current state of the game with the provided game id
    """

    def get(self, request, format=None):
        user_id = request.GET.get("game_id")

        # Get the preference
        # Get the tasks
        # Get the events

        # Build schedule obj

        # Add task to schedule

        # Save in db
        # Send to user

        # otherwise just query and send
        return Response("")


# Create your views here.
class AddTask(APIView):
    """
    Returns the current state of the game with the provided game id
    """

    def post(self, request, format=None):
        user_id = request.GET.get("game_id")

        # otherwise just query and send
        return Response("")


# Create your views here.
class AddEvent(APIView):
    """
    Returns the current state of the game with the provided game id
    """

    def post(self, request, format=None):
        user_id = request.GET.get("game_id")

        # otherwise just query and send
        return Response("")


# Create your views here.
class RemoveTask(APIView):
    """
    Returns the current state of the game with the provided game id
    """

    def post(self, request, format=None):
        user_id = request.GET.get("game_id")

        # otherwise just query and send
        return Response("")


class Schedule:

    def __init__(self, schedule_start_date, schedule_end_date, preferences, events=None, tasks=None):
        """
        Initialize a Schedule object

        Inputs:
        * start_date (datetime obj): the starting date for the schedule
        * end_date (datetime obj): the ending date for the schedule
        * preferences (dictionary): sleep and energy preferences
        * event
        """
        self.days = self.generate_blank_schedule(schedule_start_date, schedule_end_date)
        self.preferences = preferences
        self.events = []
        self.tasks = []

        if events is None:
            events = []

        if tasks is None:
            tasks = []

        self.initialize_events(events)
        self.initialize_tasks(tasks)

    def initialize_events(self, events):
        self.account_sleep()
        for event in events:
            event_obj = Event(event["name"], event["priority"], event["difficulty"], event["date"], event["start_time"],
                              event["end_time"])
            self.events.append(event_obj)

        for event in self.events:
            self.days[event.date].schedule_event(event)

    def initialize_tasks(self, tasks):
        self.sort_tasks()
        for task in tasks:
            task_obj = Task(task["name"], task["chunks"], task["priority"], task["duration"], task["difficulty"],
                            task["start_date"], task["end_date"])
            self.add_task(task_obj)

    def generate_blank_schedule(self, start_date, end_date):
        """
        Generate a blank schedule

        Input:
        * start_date (datetime obj): the starting date for the schedule
        * end_date (datetime obj): the ending date for the schedule

        Output:
        * days (dict): dictionary mapping datetime objects to Day objects
        """
        delta = datetime.timedelta(days=1)
        days = {}
        curr_date = start_date
        while curr_date <= end_date:
            days[curr_date] = Day(curr_date)
            curr_date += delta
        return days

    def sort_tasks(self):
        """
        Sort tasks by formula
        """
        tasks = []
        for task in self.tasks:
            num = .6 * task.priority + .4 * task.difficulty
            tasks.append((task, num))
        tasks.sort(key=lambda x: x[1])

        self.tasks = []
        for task in tasks:
            self.tasks.append(task[0])

    def sort_events(self):
        """
        Sort events by formula
        """
        events = []
        for event in self.events:
            num = .6 * event.priority + .4 * event.difficulty
            events.append((event, num))
        events.sort(key=lambda x: x[1])

        self.events = []
        for event in events:
            self.events.append(event[0])

    def add_task(self, task, hasSorted=False):
        """
        Add a task into the schedule

        Input:
        * task (Task obj): task information
        """
        block_size = MINUTES_PER_BLOCK if task.chunks else task.duration
        self.tasks.append(task)
        remaining_duration = task.duration
        for day, day_schedule in self.days.items():
            if day < task.start_date:
                continue
            if day > task.due_date:
                break

            while remaining_duration > 0:
                curr_duration = block_size if remaining_duration >= block_size else remaining_duration
                is_time_available, start_time = day_schedule.find_time_for_task(curr_duration)

                if not is_time_available:
                    break

                if is_time_available:
                    remaining_duration -= curr_duration
                    hour, block = start_time
                    event = day_schedule.schedule_task_to_event(task, hour, block, curr_duration)
                    self.events.append(event)

            if remaining_duration == 0:
                return

        # not able to add
        if not hasSorted:
            self.sort_tasks()
            hasSorted = True
            for task in self.tasks:
                self.add_task(task, hasSorted)
        else:
            return 'cannot add task!'

    def account_sleep(self):
        """
        Block out time for sleep in the schedule

        Input:
        * energy_preferences (list): energy preferences (0 - least to 5 - most) for every hour in the day
        """
        for time, block_energy in enumerate(self.preferences.energy_preferences):
            if block_energy == 0:
                for date, day_schedule in self.days.items():
                    event = Event('sleep', 6, 10, date, self.preferences.sleep_start, self.preferences.sleep_end)
                    self.events.append(event)

    def display_schedule(self):
        """
        Display the schedule as a 2D list
        """
        for day, day_schedule in self.days.items():
            print(day_schedule.times)


class Day:
    def __init__(self, date):
        """
        Initialize a Day object

        Inputs:
        * date (date obj): date that object represents
        """
        self.date = date
        self.times = [[None] * BLOCKS_PER_HOUR for _ in range(HOURS_PER_DAY)]

    def get_open_times(self):
        """
        Get all available time blocks

        Inputs: None

        Output:
        * open_times (list): a list of 24 sets, one for each hour, containing the timeblocks within that hour that are
        available; 0 = first fifteen minutes, 1 = second fifteen minutes, etc.
        """
        open_times = [set() for _ in range(HOURS_PER_DAY)]
        for i in range(HOURS_PER_DAY):
            for j in range(BLOCKS_PER_HOUR):
                if not self.times[i][j]:
                    open_times[i].add(j)
        return open_times

    def find_time_for_task(self, duration):
        """
        Finds first time block in which task can be scheduled

        Inputs:
        * task (Task obj): task that is to be scheduled

        Output:
        * boolean representing whether or not a time block in which task can be fit is available
        * tuple in form (hour, block) denoting first hour and 15-minute block within that hour during which
        the task can be scheduled; defaults to (0, 0) if not possible
        """
        start_time = (0, 0)
        curr_duration = 0
        open_times = self.get_open_times()
        restart_time = False
        for i, hour in enumerate(open_times):
            for block in [0, 1, 2, 3]:
                if curr_duration >= duration:
                    return True, start_time
                if block in hour:
                    if restart_time:
                        start_time = (i, block)
                        restart_time = False
                    curr_duration += 15
                else:
                    curr_duration = 0
                    restart_time = True
        return False, (0, 0)

    def time_plus(self, time, timedelta):
        start = datetime.datetime(
            2000, 1, 1,
            hour=time.hour, minute=time.minute, second=time.second)
        end = start + timedelta
        return end.time()

    def schedule_task_to_event(self, task, hour, block, duration):
        """
        Insert given task into schedule starting at designated hour and block.

        Inputs:
        * task (Task obj): the task to be scheduled
        * hour (int): the hour from 0 to 23 during which the task should be started
        * block (int): the block (0, 1, 2, etc) during the hour in which the task should be started

        Output: void
        """
        date = self.date
        start_time = datetime.time(hour, block * BLOCK_LENGTH, 0)
        end_time = self.time_plus(start_time, datetime.timedelta(minutes=duration))
        minutes_per_block = MINUTES_PER_HOUR / BLOCKS_PER_HOUR
        for i in range(int(duration // minutes_per_block)):
            self.times[hour][block] = task.name
            if block >= BLOCKS_PER_HOUR - 1:
                hour += 1
                block = 0
            else:
                block += 1

        return Event(task.name, task.priority, task.difficulty, date, start_time, end_time)

    def schedule_event(self, event):
        t1 = datetime.timedelta(hours=event.start_time.hour, minutes=event.start_time.minute)
        t2 = datetime.timedelta(hours=event.end_time.hour, minutes=event.end_time.minute)

        duration = (t2 - t1).total_seconds() / 60
        hour = event.start_time.hour
        block = event.start_time.minute
        minutes_per_block = MINUTES_PER_HOUR / BLOCKS_PER_HOUR
        for i in range(int(duration // minutes_per_block)):
            self.times[hour][block] = event.name
            if block >= BLOCKS_PER_HOUR - 1:
                hour += 1
                block = 0
            else:
                block += 1
