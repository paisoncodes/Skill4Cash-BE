from django.http.response import Http404, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from .serializers import (
    BaseUserSerializer,
    ServiceProviderSerializer
)
from .models import (
    BaseUserModel,
    ServiceProvider
)
from rest_framework.views import APIView

# Create your views here.


class Customer(APIView):
    queryset = BaseUserModel.objects.all()
    serializer_class = BaseUserSerializer

    def get(self, request):

        customers = Customer.objects.all()
        serializer = BaseUserSerializer(customers, many=True)

        return Response(serializer.data)

    
    def post(self, request):
        serializer = BaseUserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerRetrieveUpdateDelete(APIView):
    queryset = BaseUserModel.objects.all()
    serializer_class = BaseUserSerializer

    def get(self, id, request):

        customer = BaseUserModel.objects.get(id=id)
        serializer = BaseUserSerializer(customer)
        if customer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, id, request):
        customer = BaseUserModel.objects.get(id=id)
        if customer:
            serializer = BaseUserSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "Invalid User ID",
                "status": status.HTTP_404_NOT_FOUND
            })
    
    def delete(self, id, request):
        customer = BaseUserModel.objects.get(id=id)
        if customer:
            customer.delete()
            return Response({
                "message": "User deleted successfully",
                "status": status.HTTP_204_NO_CONTENT
            })
        else:
            return Response({
                "message": "Invalid User ID",
                "status": status.HTTP_404_NOT_FOUND
            })


class ServiceProvider(APIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer

    def get(self, request):

        service_providers = ServiceProvider.objects.all()
        serializer = ServiceProviderSerializer(service_providers, many=True)

        return Response(serializer.data)

    
    def post(self, request):
        serializer = ServiceProviderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceProviderRetrieveUpdateDelete(APIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer

    def get(self, id, request):

        customer = ServiceProvider.objects.get(id=id)
        serializer = ServiceProviderSerializer(customer)
        if customer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, id, request):
        customer = ServiceProvider.objects.get(id=id)
        if customer:
            serializer = ServiceProviderSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "Invalid User ID",
                "status": status.HTTP_404_NOT_FOUND
            })
    
    def delete(self, id, request):
        customer = ServiceProvider.objects.get(id=id)
        if customer:
            customer.delete()
            return Response({
                "message": "User deleted successfully",
                "status": status.HTTP_204_NO_CONTENT
            })
        else:
            return Response({
                "message": "Invalid User ID",
                "status": status.HTTP_404_NOT_FOUND
            })