from .serializers import (
    RatingSerializer,
    CategorySerializer,
    ScheduleSerializer
)

from .models import (
    Rating,
    Category,
    Schedule
)

from authentication.models import (
    ServiceProvider,
    User,
)

from rest_framework.permissions import IsAuthenticated
from src.permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist





class CreateReadReview(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()

    def get(self, request):
        ratings_seriailizers = RatingSerializer(self.queryset, many = True)

        return Response(
            ratings_seriailizers.data,
            status = status.HTTP_200_OK
        )
    
    def post(self, request):
        try:
            request.data["customer"] = User.objects.get(id=request.data["customer"])
            request.data["service_provider"] = ServiceProvider.objects.get(id=request.data["service_provider"])
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)
        serializer = RatingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status = status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )

class ReadSPReviews(APIView):
    permission_classes = (IsAuthenticated,)
    queryset = Rating.objects.all()

    def get(self, request):
        try:
            service_provider = ServiceProvider.objects.get(user=request.user)
            sp_review = Rating.objects.filter(service_provider = service_provider)
            if sp_review:
                return Response(
                    sp_review,
                    status = status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "ratings": []
                    },
                    status = status.HTTP_204_NO_CONTENT
                )
        except ObjectDoesNotExist:
            return Response(
                {
                    "message": "Service Provider does not exist"
                },
                status = status.HTTP_400_BAD_REQUEST
            )


class CreateReadCategory(APIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = CategorySerializer
    category = Category.objects.all()

    def get(self, request):
        category_serializer = CategorySerializer(self.category, many=True)
        category_list = [category["name"] for category in category_serializer.data]
        return Response(
            {"categories": category_list},
            status = status.HTTP_200_OK
        )

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        category_name = request.data["name"]

        category = Category.objects.filter(name__icontains=category_name)
        if category.exists():
            return Response(
                {"message": "category name already exists!"}
            )
            
        else:
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status = status.HTTP_201_CREATED
                )

            else:
                return Response(
                    serializer.errors,
                    status = status.HTTP_400_BAD_REQUEST
                )

class CreateReadSchedule(APIView):
    serializer_class = ScheduleSerializer
    schedules = Schedule.objects.all()

    def get(self, request):
        schedules = ScheduleSerializer(data=self.schedules, many=True)
        return Response(schedules.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        try:
            request.data["customer"] = User.objects.get(id=request.data["customer"])
            request.data["service_provider"] = ServiceProvider.objects.get(id=request.data["service_provider"])
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)
        serializer = ScheduleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status = status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )

class ReadSPSchedules(APIView):
    serializer_class = ScheduleSerializer

    def get(self, request):
        try:
            service_provider = ServiceProvider.objects.get(user=request.user)
            schedules = Schedule.objects.filter(service_provider = service_provider)
            serialized_schedules = ScheduleSerializer(data=schedules)
            if schedules:
                return Response(
                    serialized_schedules.data,
                    status = status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "schedules": []
                    },
                    status = status.HTTP_204_NO_CONTENT
                )
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)

class ReadUpdateDeleteSchedule(APIView):
    serializer_class = ScheduleSerializer

    def get(self, request, id):
        try:
            schedule = Schedule.objects.get(id=id)
            if schedule.service_provider.user == request.user:
                serialized_schedule = ScheduleSerializer(data=schedule)
                return Response(
                    serialized_schedule.data,
                    status = status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "message": "You can't view this schedule"
                    },
                    status = status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            schedule = Schedule.objects.get(id=id)
            if schedule.service_provider.user == request.user:
                request.data["title"] = "title" if request.data["title"] else schedule.title
                request.data["customer"] = schedule.customer
                request.data["date_and_time"] = "date_and_time" if request.data["date_and_time"] else schedule.date_and_time
                request.data["detail"] = "detail" if request.data["detail"] else schedule.detail
                request.data["service_provider"] = schedule.service_provider

                serialized_schedule = ScheduleSerializer(data=request.data)
                if serialized_schedule.is_valid():
                    serialized_schedule.save()
                    return Response(
                        serialized_schedule.data,
                        status = status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            "error": "Invalid input"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {
                        "message": "You can't edit this schedule"
                    },
                    status = status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)