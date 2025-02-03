import json
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiResponse
from utils.utils import UploadUtil, api_response
from .serializers import RatingSerializer, CategorySerializer, ScheduleSerializer
from .models import Rating, Schedule
from authentication.models import User, Category


class RatingViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_classes = {
        "list": RatingSerializer,
        "create": RatingSerializer,
        "retrieve_sp_reviews": RatingSerializer,
    }
    queryset = Rating.objects.all()

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @extend_schema(
        responses={200: OpenApiResponse(description="List of all ratings")},
    )
    def list(self, request):
        ratings_serializers = self.get_serializer(self.queryset, many=True)
        return Response(ratings_serializers.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=RatingSerializer,
        responses={201: OpenApiResponse(description="Rating created successfully")},
    )
    def create(self, request):
        try:
            User.objects.get(id=request.data["customer"], role="customer")
            User.objects.get(
                id=request.data["service_provider"], role="service_provider"
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Service provider reviews retrieved successfully"
            )
        },
    )
    @action(detail=False, methods=["get"])
    def retrieve_sp_reviews(self, request):
        try:
            sp_review = Rating.objects.filter(service_provider__user=request.user)
            if sp_review.exists():
                serializer = self.get_serializer(sp_review, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"ratings": []}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {"message": "Service Provider does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CategoryViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        "list": CategorySerializer,
        "create": CategorySerializer,
        "populate": CategorySerializer,
    }
    queryset = Category.objects.all()

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @extend_schema(
        responses={200: OpenApiResponse(description="List of all categories")},
    )
    def list(self, request):
        category_serializer = self.get_serializer(self.queryset, many=True)
        return api_response("Categories retrieved successfully", 200, "Success", category_serializer.data)

    @extend_schema(
        request=CategorySerializer,
        responses={201: OpenApiResponse(description="Category created successfully")},
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        category_name = request.data["name"]

        if Category.objects.filter(name__iexact=category_name).exists():
            return Response(
                {"message": "Category name already exists!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            201: OpenApiResponse(description="Categories populated successfully")
        },
    )
    @action(detail=False, methods=["post"])
    def populate(self, request):
        with open(f"{settings.PATH}/categories.json") as file:
            categories = json.load(file)
        for key in categories.keys():
            category_name = "-".join(key.split("_"))
            name = " ".join(key.split("_"))
            image_url = (
                UploadUtil.upload_category_image(
                    f"{settings.PATH}/{categories[key]}", category_name
                )
            )["image_url"]
            if Category.objects.filter(name=name).exists():
                continue
            else:
                Category.objects.create(name=name, image=image_url)
        serializer = self.get_serializer(Category.objects.all(), many=True)
        return api_response(
            "Categories uploaded successfully", 201, "Success", serializer.data
        )


class ScheduleViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_classes = {
        "list": ScheduleSerializer,
        "create": ScheduleSerializer,
        "retrieve_sp_schedules": ScheduleSerializer,
        "retrieve_update_delete": ScheduleSerializer,
    }
    queryset = Schedule.objects.all()

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    @extend_schema(
        responses={200: OpenApiResponse(description="List of all schedules")},
    )
    def list(self, request):
        schedules_serializer = self.get_serializer(self.queryset, many=True)
        return Response(schedules_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ScheduleSerializer,
        responses={201: OpenApiResponse(description="Schedule created successfully")},
    )
    def create(self, request):
        try:
            User.objects.get(id=request.data["customer"], role="customer")
            User.objects.get(
                id=request.data["service_provider"], role="service_provider"
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Service provider schedules retrieved successfully"
            )
        },
    )
    @action(detail=False, methods=["get"])
    def retrieve_sp_schedules(self, request):
        try:
            schedules = Schedule.objects.filter(service_provider__user=request.user)
            if schedules.exists():
                serializer = self.get_serializer(schedules, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"schedules": []}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={200: OpenApiResponse(description="Schedule retrieved successfully")},
    )
    def retrieve(self, request, pk=None):
        schedule = self.get_object()
        if schedule:
            if schedule.service_provider.user == request.user:
                serializer = self.get_serializer(schedule)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "You can't view this schedule"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(
            {"error": "Instance of Schedule does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @extend_schema(
        request=ScheduleSerializer,
        responses={200: OpenApiResponse(description="Schedule updated successfully")},
    )
    def update(self, request, pk=None):
        schedule = self.get_object()
        if schedule:
            if schedule.service_provider.user == request.user:
                serializer = self.get_serializer(
                    schedule, data=request.data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "You can't edit this schedule"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(
            {"error": "Instance of Schedule does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @extend_schema(
        responses={204: OpenApiResponse(description="Schedule deleted successfully")},
    )
    def destroy(self, request, pk=None):
        schedule = self.get_object()
        if schedule:
            if schedule.service_provider.user == request.user:
                schedule.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"message": "You can't delete this schedule"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(
            {"error": "Instance of Schedule does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )
