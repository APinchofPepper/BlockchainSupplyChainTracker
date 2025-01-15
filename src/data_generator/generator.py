# src/data_generator/generator.py

import random
import uuid
from datetime import datetime, timedelta
import json

class SupplyChainDataGenerator:
    def __init__(self):
        self.locations = {
            'manufacturing': [
                {'name': 'Factory A', 'location': {'lat': 31.2304, 'lng': 121.4737}},  # Shanghai
                {'name': 'Factory B', 'location': {'lat': 22.5431, 'lng': 114.0579}},  # Shenzhen
            ],
            'distribution': [
                {'name': 'Distribution Center 1', 'location': {'lat': 34.0522, 'lng': -118.2437}},  # LA
                {'name': 'Distribution Center 2', 'location': {'lat': 40.7128, 'lng': -74.0060}},   # NYC
            ],
            'retail': [
                {'name': 'Retail Store X', 'location': {'lat': 37.7749, 'lng': -122.4194}},  # SF
                {'name': 'Retail Store Y', 'location': {'lat': 41.8781, 'lng': -87.6298}},   # Chicago
            ]
        }
        
        self.products = [
            {'name': 'Laptop', 'sku': 'TECH-LP', 'category': 'Electronics'},
            {'name': 'Smartphone', 'sku': 'TECH-SP', 'category': 'Electronics'},
            {'name': 'Tablet', 'sku': 'TECH-TB', 'category': 'Electronics'},
            {'name': 'Headphones', 'sku': 'TECH-HP', 'category': 'Electronics'}
        ]
        
        self.status_flow = [
            'manufactured',
            'quality_check_passed',
            'shipped_to_distribution',
            'arrived_at_distribution',
            'shipped_to_retail',
            'arrived_at_retail',
            'sold_to_customer'
        ]

    def generate_product_journey(self, start_date=None):
        """Generate a complete journey for a single product"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))

        product = random.choice(self.products)
        product_id = str(uuid.uuid4())
        current_date = start_date
        journey = []

        # Select random locations for the journey
        manufacturer = random.choice(self.locations['manufacturing'])
        distributor = random.choice(self.locations['distribution'])
        retailer = random.choice(self.locations['retail'])

        for status in self.status_flow:
            # Add some randomness to the timing
            current_date += timedelta(hours=random.randint(4, 48))
            
            # Determine the current location and participants based on status
            if status in ['manufactured', 'quality_check_passed']:
                location = manufacturer
                from_party = manufacturer['name']
                to_party = manufacturer['name']
            elif status in ['shipped_to_distribution', 'arrived_at_distribution']:
                location = distributor if 'arrived' in status else {
                    'name': 'In Transit',
                    'location': self._interpolate_location(
                        manufacturer['location'],
                        distributor['location'],
                        0.5 if 'shipped' in status else 0.9
                    )
                }
                from_party = manufacturer['name']
                to_party = distributor['name']
            elif status in ['shipped_to_retail', 'arrived_at_retail']:
                location = retailer if 'arrived' in status else {
                    'name': 'In Transit',
                    'location': self._interpolate_location(
                        distributor['location'],
                        retailer['location'],
                        0.5 if 'shipped' in status else 0.9
                    )
                }
                from_party = distributor['name']
                to_party = retailer['name']
            else:  # sold_to_customer
                location = retailer
                from_party = retailer['name']
                to_party = 'End Customer'

            # Generate transaction data
            transaction = {
                'product_id': product_id,
                'product_name': product['name'],
                'product_sku': product['sku'],
                'product_category': product['category'],
                'timestamp': current_date.timestamp(),
                'from': from_party,
                'to': to_party,
                'status': status,
                'location': location['location'],
                'additional_data': {
                    'temperature': round(random.uniform(18, 22), 1) if 'shipped' in status else None,
                    'humidity': round(random.uniform(45, 55), 1) if 'shipped' in status else None,
                    'inspection_id': str(uuid.uuid4()) if 'quality_check' in status else None,
                    'batch_id': f"BATCH-{random.randint(1000, 9999)}",
                }
            }
            journey.append(transaction)

        return journey

    def _interpolate_location(self, start_loc, end_loc, progress):
        """Interpolate between two locations to simulate movement"""
        return {
            'lat': start_loc['lat'] + (end_loc['lat'] - start_loc['lat']) * progress,
            'lng': start_loc['lng'] + (end_loc['lng'] - start_loc['lng']) * progress
        }

    def generate_multiple_products(self, num_products=10):
        """Generate journeys for multiple products"""
        all_journeys = []
        for _ in range(num_products):
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            journey = self.generate_product_journey(start_date)
            all_journeys.extend(journey)
        
        # Sort all transactions by timestamp
        return sorted(all_journeys, key=lambda x: x['timestamp'])

if __name__ == "__main__":
    # Example usage
    generator = SupplyChainDataGenerator()
    data = generator.generate_multiple_products(3)
    print(json.dumps(data, indent=2))