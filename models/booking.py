from datetime import datetime
from enum import Enum

class BookingStatus(Enum):
    CONFIRMED = "Confirmed"
    CHECKED_IN = "Checked In"
    CHECKED_OUT = "Checked Out"
    CANCELLED = "Cancelled"

class Booking:
    def __init__(self, booking_id, guest_id, room_id, check_in, check_out, total_price):
        self.booking_id = booking_id
        self.guest_id = guest_id
        self.room_id = room_id
        self.check_in = check_in
        self.check_out = check_out
        self.total_price = total_price
        self.status = BookingStatus.CONFIRMED
        self.created_at = datetime.now()
        self.special_requests = []
    
    def get_duration(self):
        return (self.check_out - self.check_in).days
    
    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'guest_id': self.guest_id,
            'room_id': self.room_id,
            'check_in': self.check_in.isoformat(),
            'check_out': self.check_out.isoformat(),
            'total_price': self.total_price,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'special_requests': self.special_requests
        }
    
    @staticmethod
    def from_dict(data):
        booking = Booking(
            booking_id=data['booking_id'],
            guest_id=data['guest_id'],
            room_id=data['room_id'],
            check_in=datetime.fromisoformat(data['check_in']),
            check_out=datetime.fromisoformat(data['check_out']),
            total_price=data['total_price']
        )
        booking.status = BookingStatus(data['status'])
        booking.created_at = datetime.fromisoformat(data['created_at'])
        booking.special_requests = data.get('special_requests', [])
        return booking
    
    def __repr__(self):
        return f"Booking({self.booking_id}, Room:{self.room_id}, {self.check_in.date()}-{self.check_out.date()})"