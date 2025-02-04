import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer


class ListingViewSet(ModelViewSet):
    '''
    ViewSet for managing Listing objects.
    Provides CRUD operations.
    '''
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(ModelViewSet):
    '''
    ViewSet for managing Booking objects.
    Provides CRUD operations.
    '''
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(user=request.user)

        # Initiate payment process
        return Response({
            'message': 'Booking created. Please complete payment',
            'payment_url': reverse('initiate-payment', args=[booking.id])
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        # Trigger async email task
        send_booking_confirmation.delay(booking.id)


class InitiatePayment(APIView):
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            amount = booking.listing.price_per_night

            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "amount": str(amount),
                "currency": "ETB",
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "tx_ref": f"alxtravel-{booking_id}-{uuid.uuid4().hex}",
                "callback_url": settings.CHAPA_WEBHOOK_URL,
                "return_url": f"https://your-frontend.com/bookings/{booking_id}/status"
            }

            response = requests.post(
                settings.CHAPA_API_URL,
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                Payment.objects.create(
                    booking=booking,
                    amount=amount,
                    chapa_tx_ref=payload['tx_ref'],
                    transaction_id=data.get('data', {}).get('id'),
                )
                return Response({
                    'payment_url': data['data']['checkout_url'],
                    'tx_ref': payload['tx_ref']
                }, status=status.HTTP_201_CREATED)

            return Response(response.json(), status=response.status_code)

        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class VerifyPayment(APIView):
    def get(self, request, tx_ref):
        try:
            payment = Payment.objects.get(chapa_tx_ref=tx_ref)
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
            }

            response = requests.get(
                f"{settings.CHAPA_API_URL}/verify/{tx_ref}",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                payment.status = 'completed' if data['status'] == 'success' else 'failed'
                payment.transaction_id = data['data']['id']
                payment.save()

                if payment.status == 'completed':
                    # Trigger confirmation email
                    send_booking_confirmation.delay(payment.booking.id)

                return Response(data)

            return Response(response.json(), status=response.status_code)

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
