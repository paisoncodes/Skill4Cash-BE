from .serializers import (
    RatingSerializer,
    CategorySerializer
)

from .models import (
    Rating,
    Category
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
        sp_id = request.GET.get("sp_id")
        try:
            service_provider = ServiceProvider.objects.get(id=sp_id)
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
            {"category": category_list},
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