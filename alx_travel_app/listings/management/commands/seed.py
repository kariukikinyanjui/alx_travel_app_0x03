
from django.core.management.base import BaseCommand
from listings.models import Listing


class Command(BaseCommand):
    help = 'Seed the database with sample listings data'

    def handle(self, *args, **kwargs):
        sample_listings = [
            {
                "title": "Cozy Cottage",
                "description": "A lovely cottage in the countryside."
                "location": "Countryside",
                "price_per_night": 120.00,
                "available": True,
            },
            {
                "title": "Luxury Apartment",
                "description": "A luxurious apartment in the city center."
                "location": "City Center",
                "price_per_night": 250.00,
                "available": True,
            },
            {
                "title": "Beach House",
                "description": "A beautiful house by the beach.",
                "location": "Beachfront",
                "price_per_night": 300.00,
                "available": True,
            },
        ]

        for listing_data in sample_listings:
            Listing.objects.create(**listing_data)

        self.stdout.write(self.style.SUCCESS("Database seeded with sample listings data."))
