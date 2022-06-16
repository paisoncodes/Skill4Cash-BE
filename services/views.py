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
from random import choice
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated, AllowAny
from src.permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema


class CreateReadReview(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer
    ratings = Rating.objects.all()

    def get(self, request):
        ratings_seriailizers = RatingSerializer(self.ratings, many=True)

        return Response(
            ratings_seriailizers.data,
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        try:
            customer = User.objects.get(id=request.data["customer"])
            service_provider = ServiceProvider.objects.get(
                id=request.data["service_provider"])
        except Exception as e:
            return Response({"error": e},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class ReadSPReviews(APIView):
    permission_classes = (IsAuthenticated,)
    queryset = Rating.objects.all()

    def get(self, request):
        try:
            sp_review = Rating.objects.filter(
                service_provider__user=request.user)
            if sp_review.exists():
                return Response(
                    sp_review,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "ratings": []
                    },
                    status=status.HTTP_204_NO_CONTENT
                )
        except ObjectDoesNotExist:
            return Response(
                {
                    "message": "Service Provider does not exist"
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CreateReadCategory(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CategorySerializer
    category = Category.objects.all()

    def get(self, request):
        category_serializer = CategorySerializer(self.category, many=True)
        category_list = [category["name"]
                         for category in category_serializer.data]
        return Response(
            {"categories": category_list},
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        category_name = request.data["name"]

        category = Category.objects.filter(name__iexact=category_name)
        if category.exists():
            return Response(
                {"message": "category name already exists!"}
            )

        else:
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )


class CreateReadSchedule(APIView):
    serializer_class = ScheduleSerializer
    permission_classes = (IsAuthenticated,)
    schedules = Schedule.objects.all()

    def get(self, request):
        schedules = ScheduleSerializer(self.schedules, many=True)
        return Response(schedules.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        try:
            customers = User.objects.get(id=request.data["customer"])
            service_providers = ServiceProvider.objects.get(
                id=request.data["service_provider"])
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)

        serializer = ScheduleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class ReadSPSchedules(APIView):
    serializer_class = ScheduleSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            schedules = Schedule.objects.filter(
                service_provider__user=request.user)

            if schedules.exists():
                serialized_schedules = ScheduleSerializer(schedules)
                return Response(
                    serialized_schedules.data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "schedules": []
                    },
                    status=status.HTTP_204_NO_CONTENT
                )
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)


class ReadUpdateDeleteSchedule(APIView):
    serializer_class = ScheduleSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, id):
        try:
            return Schedule.objects.get(id=id)
        except Schedule.DoesNotExist:
            return None

    def get(self, request, id):

        if (schedule := self.get_object(id)):

            if schedule.service_provider.user == request.user:
                serialized_schedule = ScheduleSerializer(schedule, many=False)

                return Response(
                    serialized_schedule.data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "message": "You can't view this schedule"
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response({"error": 'Instance of User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request, id):

        if (schedule := self.get_object(id)):

            if schedule.service_provider.user == request.user:
                customer = request.data['customer'] if 'customer' in request.data.keys() else schedule.customer
                service_provider = request.data["service_provider"] if 'customer' in request.data.keys() else schedule.service_provider

                serialized_schedule = ScheduleSerializer(
                    schedule, data=request.data)

                if serialized_schedule.is_valid():
                    serialized_schedule.save()

                    return Response(
                        serialized_schedule.data,
                        status=status.HTTP_200_OK
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
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response({"error": 'Instance of User does not exist'}, status=status.HTTP_404_NOT_FOUND)

# function to populate


class PopulateData(APIView):

    permission_classes = (AllowAny,)

    def get(self, request):

        name = 'Electrician FashionDesigner WebDeveloper Marketer Contentwriter'.split()
        title = 'Meeting Advert Picnic Social Outing'.split()
        service_provider = ServiceProvider.objects.all()
        customer = User.objects.filter(role='customer')
        rating = [x for x in range(10)]

        if not Category.objects.all():
            for x in range(1, 11):
                Category.objects.create(name=f'{choice(name)} {x}')
                Rating.objects.create(
                    service_provider=choice(service_provider),
                    rating=choice(rating),
                    review='This is good :)',
                    customer=choice(customer)
                )
                Schedule.objects.create(
                    title=choice(title),
                    service_provider=choice(service_provider),
                    customer=choice(customer),
                    date_and_time=timezone.now(),
                    detail="Keep on update on all upcoming schedules"
                )
        return Response({'message': 'Data populated sucessfully'})
