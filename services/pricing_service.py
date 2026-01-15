from datetime import datetime, timedelta

class PricingService:
    def __init__(self):
        self.weekend_multiplier = 1.2
        self.holiday_multiplier = 1.5
        self.seasonal_multipliers = {
            'peak': 1.3,
            'normal': 1.0,
            'off': 0.8
        }
    
    def calculate_price(self, room, check_in, check_out):
        """Calculate total price with dynamic pricing"""
        days = (check_out - check_in).days
        base_price = room.base_price
        total = 0
        
        current_date = check_in
        for _ in range(days):
            day_price = base_price
            
            # Weekend pricing
            if current_date.weekday() >= 5:
                day_price *= self.weekend_multiplier
            
            # Seasonal pricing
            season = self._get_season(current_date)
            day_price *= self.seasonal_multipliers[season]
            
            total += day_price
            current_date = current_date + timedelta(days=1)
        
        return round(total, 2)
    
    def _get_season(self, date):
        """Determine season"""
        month = date.month
        if month in [12, 1, 2, 6, 7]:
            return 'peak'
        elif month in [4, 5, 10, 11]:
            return 'off'
        else:
            return 'normal'
    
    def apply_loyalty_discount(self, price, loyalty_tier):
        """Apply loyalty discount"""
        discounts = {
            'None': 0,
            'Bronze': 0.05,
            'Silver': 0.10,
            'Gold': 0.15,
            'Platinum': 0.20
        }
        discount = discounts.get(loyalty_tier, 0)
        return round(price * (1 - discount), 2)