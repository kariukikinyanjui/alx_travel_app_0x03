from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking


@shared_task
def send_booking_confirmation(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        subject = f'Booking Confirmation #{booking.id}'
        message = f'''Hello {booking.user.username},
        Your booking for {booking_listing.title} is confirmed.
        Check-in: {booking.check_in_date}
        Check-out: {booking.check_out_date}

        Thank you for choosing ALX Travel!'''

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            fail_silently=False,
        )
        return f"Email sent to {booking.user.email}"
    except Booking.DoesNotExist:
        return "Booking not found"


