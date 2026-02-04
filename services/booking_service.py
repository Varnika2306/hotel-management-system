from datetime import datetime
from models.booking import Booking, BookingStatus
from data_structures.interval_tree import IntervalTree
import json
import os

class BookingService:
    def __init__(self):
        self.bookings = {}
        self.room_trees = {}
        self.booking_counter = 1
    
    def create_booking(self, guest_id, room_id, check_in, check_out, total_price):
        """Create a new booking"""
        if check_in >= check_out:
            raise ValueError("Check-in date must be before check-out date")
        
        # Check if room is available
        if room_id in self.room_trees:
            overlaps = self.room_trees[room_id].search(check_in, check_out)
            if overlaps:
                raise ValueError("Room is not available for the selected dates")
        
        # Create booking
        booking_id = f"B{self.booking_counter:06d}"
        self.booking_counter += 1
        
        booking = Booking(
            booking_id=booking_id,
            guest_id=guest_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price
        )
        
        self.bookings[booking_id] = booking
        
        # Add to interval tree
        if room_id not in self.room_trees:
            self.room_trees[room_id] = IntervalTree()
        
        self.room_trees[room_id].insert(check_in, check_out, booking_id)
        
        return booking
    
    def cancel_booking(self, booking_id):
        """Cancel a booking"""
        if booking_id not in self.bookings:
            raise ValueError("Booking not found")
        
        booking = self.bookings[booking_id]
        
        if booking.status == BookingStatus.CANCELLED:
            raise ValueError("Booking is already cancelled")
        
        booking.cancel()
        
        # Remove from interval tree (just mark as cancelled, don't actually remove)
        # In a real system, you might want to physically remove it from the tree
        
        return booking
    
    def get_booking(self, booking_id):
        """Get a booking by ID"""
        return self.bookings.get(booking_id)
    
    def get_all_bookings(self):
        """Get all bookings"""
        return list(self.bookings.values())
    
    def find_available_rooms(self, check_in, check_out, rooms):
        """Find available rooms for given dates"""
        available_rooms = []
        
        for room in rooms:
            if room.room_id not in self.room_trees:
                available_rooms.append(room)
            else:
                overlaps = self.room_trees[room.room_id].search(check_in, check_out)
                # Filter out cancelled bookings
                active_overlaps = [
                    o for o in overlaps 
                    if self.bookings[o].status != BookingStatus.CANCELLED
                ]
                if not active_overlaps:
                    available_rooms.append(room)
        
        return available_rooms
    
    def save_to_file(self, filename='data/bookings.json'):
        """Save bookings to JSON file"""
        os.makedirs('data', exist_ok=True)
        
        data = {
            'booking_counter': self.booking_counter,
            'bookings': {bid: b.to_dict() for bid, b in self.bookings.items()}
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename='data/bookings.json'):
        """Load bookings from JSON file"""
        try:
            if not os.path.exists(filename):
                # File doesn't exist, that's okay - we'll start fresh
                return
            
            # Check if file is empty
            if os.path.getsize(filename) == 0:
                # File is empty, that's okay - we'll start fresh
                return
            
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.booking_counter = data.get('booking_counter', 1)
            
            # Load bookings
            for bid, b_data in data.get('bookings', {}).items():
                booking = Booking.from_dict(b_data)
                self.bookings[bid] = booking
                
                # Rebuild interval trees for active bookings
                if booking.status != BookingStatus.CANCELLED:
                    if booking.room_id not in self.room_trees:
                        self.room_trees[booking.room_id] = IntervalTree()
                    
                    self.room_trees[booking.room_id].insert(
                        booking.check_in, 
                        booking.check_out, 
                        booking.booking_id
                    )
        
        except json.JSONDecodeError:
            # JSON is corrupted, start fresh
            print(f"Warning: {filename} is corrupted. Starting with empty bookings.")
            self.bookings = {}
            self.room_trees = {}
            self.booking_counter = 1
        
        except Exception as e:
            # Any other error, print and start fresh
            print(f"Warning: Error loading {filename}: {e}. Starting with empty bookings.")
            self.bookings = {}
            self.room_trees = {}
            self.booking_counter = 1
