from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Listing, Booking
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
