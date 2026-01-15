from enum import Enum

class RoomType(Enum):
    STANDARD = "Standard"
    DELUXE = "Deluxe"
    SUITE = "Suite"
    PENTHOUSE = "Penthouse"

class RoomStatus(Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    CLEANING = "Cleaning"
    MAINTENANCE = "Maintenance"

class Room:
    def __init__(self, room_id, room_number, room_type, floor, base_price, features=None):
        self.room_id = room_id
        self.room_number = room_number
        self.room_type = room_type
        self.floor = floor
        self.base_price = base_price
        self.features = features or []
        self.status = RoomStatus.AVAILABLE
    
    def to_dict(self):
        return {
            'room_id': self.room_id,
            'room_number': self.room_number,
            'room_type': self.room_type.value,
            'floor': self.floor,
            'base_price': self.base_price,
            'features': self.features,
            'status': self.status.value
        }
    
    @staticmethod
    def from_dict(data):
        room = Room(
            room_id=data['room_id'],
            room_number=data['room_number'],
            room_type=RoomType(data['room_type']),
            floor=data['floor'],
            base_price=data['base_price'],
            features=data.get('features', [])
        )
        room.status = RoomStatus(data.get('status', 'Available'))
        return room
    
    def __repr__(self):
        return f"Room({self.room_number}, {self.room_type.value}, ${self.base_price})"