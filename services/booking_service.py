from datetime import datetime
from data_structures.interval_tree import IntervalTree, Interval
from models.booking import Booking, BookingStatus
import json
import os

class BookingService:
    def __init__(self):
        self.room_trees = {}
        self.bookings = {}
        self.booking_counter = 1
    
    def initialize_room(self, room_id):
        if room_id not in self.room_trees:
            self.room_trees[room_id] = IntervalTree()
    
    def check_availability(self, room_id, check_in, check_out):
        """Check if room is available"""
        if room_id not in self.room_trees:
            return True
        
        query = Interval(check_in, check_out, "QUERY", room_id)
        overlaps = self.room_trees[room_id].search_overlaps(query)
        return len(overlaps) == 0
    
    def find_available_rooms(self, check_in, check_out, room_list):
        """Find all available rooms for dates"""
        available = []
        for room in room_list:
            if self.check_availability(room.room_id, check_in, check_out):
                available.append(room)
        return available
    
    def create_booking(self, guest_id, room_id, check_in, check_out, total_price):
        """Create new booking"""
        if not self.check_availability(room_id, check_in, check_out):
            raise ValueError(f"Room {room_id} not available")
        
        booking_id = f"BK{self.booking_counter:05d}"
        self.booking_counter += 1
        
        booking = Booking(booking_id, guest_id, room_id, check_in, check_out, total_price)
        self.bookings[booking_id] = booking
        
        self.initialize_room(room_id)
        interval = Interval(check_in, check_out, booking_id, room_id)
        self.room_trees[room_id].insert(interval)
        
        return booking
    
    def cancel_booking(self, booking_id):
        """Cancel booking"""
        if booking_id not in self.bookings:
            raise ValueError(f"Booking {booking_id} not found")
        
        booking = self.bookings[booking_id]
        booking.status = BookingStatus.CANCELLED
        
        interval = Interval(booking.check_in, booking.check_out, booking_id, booking.room_id)
        self.room_trees[booking.room_id].delete(interval)
        
        return booking
    
    def get_all_bookings(self):
        """Get all bookings"""
        return list(self.bookings.values())
    
    def get_booking(self, booking_id):
        """Get specific booking"""
        return self.bookings.get(booking_id)
    
    def save_to_file(self, filename='data/bookings.json'):
        """Save bookings"""
        os.makedirs('data', exist_ok=True)
        data = {bid: booking.to_dict() for bid, booking in self.bookings.items()}
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename='data/bookings.json'):
        """Load bookings"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            for booking_data in data.values():
                booking = Booking.from_dict(booking_data)
                self.bookings[booking.booking_id] = booking
                
                # Rebuild interval trees
                if booking.status != BookingStatus.CANCELLED:
                    self.initialize_room(booking.room_id)
                    interval = Interval(booking.check_in, booking.check_out,
                                      booking.booking_id, booking.room_id)
                    self.room_trees[booking.room_id].insert(interval)
                
                # Update counter
                booking_num = int(booking.booking_id.replace('BK', ''))
                self.booking_counter = max(self.booking_counter, booking_num + 1)
        except FileNotFoundError:
            pass