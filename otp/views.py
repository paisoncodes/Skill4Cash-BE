from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from src.utils import send_otp, otp_session
from rest_framework.views import APIView
from .serializers import OTPSerializers
from authentication.models import User
from . models import OTPVerification
from rest_framework import status
import jwt


class ReadUpdatePhoneView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            queryset = OTPVerification.objects.get(user=request.user)
            serializers = OTPSerializers(queryset, many=False)
            return Response(serializers.data, status=status.HTTP_200_OK)

        except OTPVerification.DoesNotExist:
            return Response({'message': 'Instance of the object does not exist', 'status': status.HTTP_404_NOT_FOUND})
        except jwt.ExpiredSignatureError:
            return Response({"status": 'OTP link expired'})

    def put(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            instance = OTPVerification.objects.get(user=user)

            # not yet updated, number yet to be updated
            new_phone_num = request.data.get('number')

            if not 'code' in request.session.keys():
                if new_phone_num:

                    if otp_session(request, str(new_phone_num), instance):
                        return Response({'status': status.HTTP_200_OK, 'message': 'OTP sent successfully'})
                    else:
                        return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Sending OTP Error'})

                else:
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid Number'})
            else:
                request.session.clear()
                if otp_session(request, new_phone_num, instance):
                    return Response({'status': status.HTTP_200_OK, 'message': 'OTP sent successfully'})
                return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Sending OTP Error'})
        except jwt.ExpiredSignatureError:
            return Response({"status": 'OTP link expired'})

    def post(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            instance = OTPVerification.objects.get(user=user)

            # getting otp code from the user
            otp = request.data.get('otp')

            if 'code' in request.session.keys():
                if str(otp) == request.session['code']:
                    updated_num = request.session['num']

                    if not User.objects.filter(
                            phone_number__iexact=updated_num).exists():
                        user.phone_number = updated_num
                        instance.phone_num = updated_num
                        instance.otp = otp
                        instance.is_validated = True
                        user.save()
                        instance.save()

                        request.session.clear()
                        return Response({'status': status.HTTP_200_OK, 'message': 'Number Changed'})
                    else:
                        request.session.clear()
                        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Number Already Exist'})
                else:
                    request.session.clear()
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid OTP'})
            else:
                return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'OTP Expired'})

        except jwt.ExpiredSignatureError:
            return Response({"status": 'OTP link expired'})


class OTPValidatePhoneView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            # matching the phone number to the session user
            user = User.objects.get(id=request.user.id)
            user_phone_num = str(user.phone_number)

            if user_phone_num:
                instance = OTPVerification.objects.get(
                    user__id=request.user.id)
                otp_validated, number = instance.is_validated, str(
                    instance.phone_num)

                if otp_validated == False and number != user_phone_num:
                    # sending otp code
                    otp_code = send_otp(user_phone_num)

                    if otp_code:
                        instance.otp = otp_code
                        instance.save()
                        return Response({'status': status.HTTP_200_OK, 'message': 'OTP sent successfully'})

                    else:
                        return Response({'status': status.HTTP_400_BAD_REQUEST, "message": 'Sending OTP Error'})

                else:
                    return Response({'status': status.HTTP_403_FORBIDDEN, 'message': 'Phone number already validated'})
            else:
                return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Invalid number given'})
        except User.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Instance of the object does not exist'})
        except jwt.ExpiredSignatureError:
            return Response({"message": 'OTP link expired'})

    def post(self, request):
        try:
            user = request.user
            user_number = User.objects.get(id=user.id).phone_number
            otp_sent = request.data.get('otp')
        except:
            return Response({'status': status.HTTP_401_UNAUTHORIZED, 'message': 'Instance of User must be authenticated'})

        if user_number and otp_sent:
            user_number, otp_sent = str(user_number), str(otp_sent)
            try:
                instance = OTPVerification.objects.get(
                    user__phone_number__iexact=user_number)
                if not instance.is_validated:
                    otp = instance.otp
                    if otp_sent == str(otp):
                        instance.phone_num = user_number
                        instance.is_validated = True
                        instance.save()
                        return Response({'status': status.HTTP_200_OK, 'message': 'OTP Code Verified'})
                    else:
                        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'OTP Incorrect!'})
                else:
                    return Response({'status': status.HTTP_403_FORBIDDEN, 'message': 'Phone number already validated'})
            except OTPVerification.DoesNotExist:
                return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Instance of the object does not exist'})
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid Entering'})
