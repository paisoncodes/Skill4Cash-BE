from authentication.serializers import LgaSerializer, StateSerializer
from rest_framework.decorators import api_view
from utils.models import Lga, State
from utils.utils import api_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema




@api_view(["GET"])
def get_states(request):
    states = State.objects.all()
    serialzier = StateSerializer(states, many=True)

    return api_response("States fetched", serialzier.data, True, 200)

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