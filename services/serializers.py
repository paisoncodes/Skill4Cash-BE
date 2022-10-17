from rest_framework import serializers
from .models import (
    Rating,
    Schedule
)
from authentication.models import Category




class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("service_provider", "rating", "review", "customer")
        read_only_fields = ("id",)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

        extra_kwargs = {
        "name": {"required": False},
        "image": {"required": False}
        }

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ("title", "customer", "date_and_time", "detail", "service_provider")
        read_only_fields = ('id',)