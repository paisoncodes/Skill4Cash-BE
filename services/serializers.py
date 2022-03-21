from rest_framework import serializers
from .models import (
    Rating,
    Category
)







class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("service_provider", "rating", "review", "customer")
    
    def create(self, validated_data):
        rating = Rating.objects.create(
            service_provider = validated_data["service_provider"],
            rating = validated_data["rating"],
            review = validated_data["review"],
            customer = validated_data["customer"]
        )

        rating.save()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"