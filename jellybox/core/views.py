from rest_framework.response import Response
from rest_framework.views import APIView


class SetPreference(APIView):
    """
    Returns the current state of the game with the provided game id
    """

    def post(self, request, format=None):
        user_id = request.GET.get("game_id")

        # otherwise just query and send
        return Response("")


class GetSchedule(APIView):
    """
    Returns the current state of the game with the provided game id
    """

    def get(self, request, format=None):
        user_id = request.GET.get("game_id")

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
