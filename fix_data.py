"""
Fix Data Files Script
This script will clean up any corrupted or empty JSON files
"""

import os
import json

def fix_data_files():
    """Fix all data files"""
    data_dir = 'data'
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    files_to_fix = ['bookings.json', 'rooms.json', 'guests.json']
    
    for filename in files_to_fix:
        filepath = os.path.join(data_dir, filename)
        
        print(f"Checking {filename}...")
        
        # If file doesn't exist or is empty, create empty JSON
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            print(f"  → Creating empty {filename}")
            
            if filename == 'bookings.json':
                default_data = {
                    'booking_counter': 1,
                    'bookings': {}
                }
            elif filename == 'guests.json':
                default_data = {}
            elif filename == 'rooms.json':
                default_data = []
            
            with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=2)
            
            print(f"  ✓ Fixed {filename}")
        
        else:
            # Try to load and verify JSON
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                print(f"  ✓ {filename} is valid")
            
            except json.JSONDecodeError:
                print(f"  → {filename} is corrupted, recreating...")
                
                if filename == 'bookings.json':
                    default_data = {
                        'booking_counter': 1,
                        'bookings': {}
                    }
                elif filename == 'guests.json':
                    default_data = {}
                elif filename == 'rooms.json':
                    default_data = []
                
                with open(filepath, 'w') as f:
                    json.dump(default_data, f, indent=2)
                
                print(f"  ✓ Fixed {filename}")

if __name__ == '__main__':
    print("=" * 50)
    print("Hotel Management System - Data File Fixer")
    print("=" * 50)
    print()
    
    fix_data_files()
    
    print()
    print("=" * 50)
    print("All data files fixed! You can now run the app.")
    print("=" * 50)
