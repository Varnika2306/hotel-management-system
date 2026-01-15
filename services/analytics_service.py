from datetime import datetime, timedelta
from collections import defaultdict

class AnalyticsService:
    def __init__(self, booking_service, rooms):
        self.booking_service = booking_service
        self.rooms = {r.room_id: r for r in rooms}
    
    def get_occupancy_rate(self, start_date, end_date):
        """Calculate occupancy rate"""
        total_room_nights = len(self.rooms) * (end_date - start_date).days
        occupied_nights = 0
        
        for booking in self.booking_service.get_all_bookings():
            if booking.status.value == "Cancelled":
                continue
            
            overlap_start = max(booking.check_in, start_date)
            overlap_end = min(booking.check_out, end_date)
            
            if overlap_start < overlap_end:
                occupied_nights += (overlap_end - overlap_start).days
        
        return (occupied_nights / total_room_nights * 100) if total_room_nights > 0 else 0
    
    def get_revenue(self, start_date, end_date):
        """Calculate total revenue"""
        total = 0
        for booking in self.booking_service.get_all_bookings():
            if booking.status.value != "Cancelled":
                if start_date <= booking.check_in < end_date:
                    total += booking.total_price
        return total
    
    def get_room_type_distribution(self):
        """Get bookings by room type"""
        distribution = defaultdict(int)
        for booking in self.booking_service.get_all_bookings():
            if booking.status.value != "Cancelled":
                room = self.rooms.get(booking.room_id)
                if room:
                    distribution[room.room_type.value] += 1
        return dict(distribution)
    
    def get_booking_stats(self):
        """Get overall statistics"""
        bookings = self.booking_service.get_all_bookings()
        total = len(bookings)
        confirmed = sum(1 for b in bookings if b.status.value == "Confirmed")
        cancelled = sum(1 for b in bookings if b.status.value == "Cancelled")
        checked_in = sum(1 for b in bookings if b.status.value == "Checked In")
        
        return {
            'total': total,
            'confirmed': confirmed,
            'cancelled': cancelled,
            'checked_in': checked_in
        }