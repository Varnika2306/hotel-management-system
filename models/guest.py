from enum import Enum
from datetime import datetime

class LoyaltyTier(Enum):
    NONE = "None"
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"

class Guest:
    def __init__(self, guest_id, name, email, phone, id_proof):
        self.guest_id = guest_id
        self.name = name
        self.email = email
        self.phone = phone
        self.id_proof = id_proof
        self.loyalty_tier = LoyaltyTier.NONE
        self.loyalty_points = 0
        self.booking_history = []
        self.preferences = {}
        self.created_at = datetime.now()
    
    def add_loyalty_points(self, points):
        self.loyalty_points += points
        self._update_tier()
    
    def _update_tier(self):
        if self.loyalty_points >= 10000:
            self.loyalty_tier = LoyaltyTier.PLATINUM
        elif self.loyalty_points >= 5000:
            self.loyalty_tier = LoyaltyTier.GOLD
        elif self.loyalty_points >= 2000:
            self.loyalty_tier = LoyaltyTier.SILVER
        elif self.loyalty_points >= 500:
            self.loyalty_tier = LoyaltyTier.BRONZE
    
    def to_dict(self):
        return {
            'guest_id': self.guest_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'id_proof': self.id_proof,
            'loyalty_tier': self.loyalty_tier.value,
            'loyalty_points': self.loyalty_points,
            'booking_history': self.booking_history,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        guest = Guest(
            guest_id=data['guest_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            id_proof=data['id_proof']
        )
        guest.loyalty_tier = LoyaltyTier(data.get('loyalty_tier', 'None'))
        guest.loyalty_points = data.get('loyalty_points', 0)
        guest.booking_history = data.get('booking_history', [])
        guest.preferences = data.get('preferences', {})
        return guest
    
    def __repr__(self):
        return f"Guest({self.name}, {self.loyalty_tier.value})"