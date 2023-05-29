from authentication.serializers import LgaSerializer, StateSerializer
from rest_framework.decorators import api_view
from utils.models import Lga, State
from utils.utils import api_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import requests




@api_view(["GET"])
def get_states(request):
    states = State.objects.all()
    serialzier = StateSerializer(states, many=True)

    return api_response("States fetched", serialzier.data, True, 200)

@api_view(["POST"])
def populate_states_and_lga(request):
    url_1 = "https://api.facts.ng/v1/states/"
    response = requests.request("GET", url_1)
    for state in response.json():
        state_, created_ = State.objects.get_or_create(state=state["name"])
        lgas = (requests.request("GET", state["uri"])).json()
        for lga in lgas["lgas"]:
            lga__, created__ = Lga.objects.get_or_create(lga=lga, state=state_)
    abuja, created = State.objects.get_or_create(state="FCT")
    _lgas = ["Abaji", "Municipal", "Bwari", "Gwagwalada", "Kuje", "Kwali"]
    for _lga in _lgas:
        __lga, __create = Lga.objects.get_or_create(lga=_lga, state=abuja)

    return api_response("States and Lgas updated", {}, True, 200)

state = openapi.Parameter('state', openapi.IN_QUERY,
                             description="State you want to retrieve lgas from.",
                             type=openapi.TYPE_STRING, required=True)

@swagger_auto_schema(manual_parameters=[state], method='get')
@api_view(["GET"])
def get_lgas(request):
    state = request.GET.get('state', None)
    lgas = Lga.objects.filter(state__state__icontains=state)
    serialzier = LgaSerializer(lgas, many=True)

    return api_response("Lgas fetched", serialzier.data, True, 200)