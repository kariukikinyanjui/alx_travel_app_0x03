from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from .tasks import send_booking_confirmation


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

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        # Trigger async email task
        send_booking_confirmation.delay(booking.id)
