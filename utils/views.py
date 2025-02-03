from rest_framework import viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from utils.utils import api_response
from authentication.serializers import LgaSerializer, StateSerializer
from utils.models import Lga, State


class StateViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        "list": StateSerializer,
    }
    queryset = State.objects.all()

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @extend_schema(
        responses={200: OpenApiResponse(description="List of all states")},
    )
    def list(self, request):
        serializer = self.get_serializer(self.queryset, many=True)
        return api_response("States fetched", serializer.data, True, 200)


class LgaViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        "list": LgaSerializer,
    }
    queryset = Lga.objects.all()

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="state",
                description="State you want to retrieve LGAs from.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            )
        ],
        responses={200: OpenApiResponse(description="List of LGAs for a given state")},
    )
    def list(self, request):
        state = request.query_params.get("state", None)
        if not state:
            return api_response("State parameter is required", {}, False, 400)

        lgas = Lga.objects.filter(state__state__icontains=state)
        serializer = self.get_serializer(lgas, many=True)
        return api_response("LGAs fetched", serializer.data, True, 200)
