from django.http.response import Http404, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from .serializers import (
    CustomerRegistrationSerializer,
    SPRegistrationSerializer
)
from .models import (
    Customer,
    ServiceProvider
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.


class CustomerRegister(APIView):
    permission_classes=(AllowAny,)
    queryset = Customer.objects.all()
    serializer_class = CustomerRegistrationSerializer
    
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Not in use yet. Still needs to be fixed.
class CustomerRetrieveUpdateDelete(APIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerRegistrationSerializer

    def get(self, id, request):

        customer = Customer.objects.get(id=id)
        serializer = CustomerRegistrationSerializer(customer)
        if customer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, id, request):
        customer = Customer.objects.get(id=id)
        if customer:
            serializer = CustomerRegistrationSerializer(customer, data=request.data)
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
        customer = Customer.objects.get(id=id)
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


class ServiceProviderRegister(APIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = SPRegistrationSerializer

    
    def post(self, request):
        serializer = SPRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Not in use yet. Still needs to be fixed.
class ServiceProviderRetrieveUpdateDelete(APIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = SPRegistrationSerializer

    def get(self, id, request):

        customer = ServiceProvider.objects.get(id=id)
        serializer = SPRegistrationSerializer(customer)
        if customer:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, id, request):
        customer = ServiceProvider.objects.get(id=id)
        if customer:
            serializer = SPRegistrationSerializer(customer, data=request.data)
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