import random
import uuid
from datetime import datetime, timedelta
import json
from math import radians, sin, cos, sqrt, atan2

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

        # Define possible supply chain issues
        self.possible_issues = [
            {
                'type': 'manufacturing_defect',
                'description': 'Quality control detected manufacturing defect',
                'delay': (2, 48),  # hours range
                'probability': 0.15
            },
            {
                'type': 'shipping_delay',
                'description': 'Weather-related shipping delay',
                'delay': (12, 72),
                'probability': 0.2
            },
            {
                'type': 'customs_inspection',
                'description': 'Extended customs inspection required',
                'delay': (24, 96),
                'probability': 0.1
            },
            {
                'type': 'port_congestion',
                'description': 'Port congestion causing delays',
                'delay': (48, 120),
                'probability': 0.15
            }
        ]

    def calculate_distance(self, loc1, loc2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1 = radians(loc1['lat']), radians(loc1['lng'])
        lat2, lon2 = radians(loc2['lat']), radians(loc2['lng'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return distance

    def calculate_shipping_time(self, distance, has_issue=False):
        """Calculate shipping time based on distance and potential issues"""
        # Base shipping speed (km/h) - varies by transport type
        base_speed = random.uniform(30, 60)  # Average speed including stops
        
        # Base shipping time in hours
        base_time = distance / base_speed
        
        # Add random variation (±20%)
        variation = random.uniform(0.8, 1.2)
        shipping_time = base_time * variation
        
        # If there's an issue, add extra delay
        if has_issue:
            issue = random.choice(self.possible_issues)
            min_delay, max_delay = issue['delay']
            extra_delay = random.uniform(min_delay, max_delay)
            shipping_time += extra_delay
        
        return shipping_time

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

        # Track if there's a current issue being handled
        current_issue = None

        for idx, status in enumerate(self.status_flow):
            # Calculate delay before creating the transaction
            delay_hours = 0
            
            # Base delays for each stage
            if status == 'manufactured':
                delay_hours = random.uniform(2, 4)  # Manufacturing: 2-4 hours
            elif status == 'quality_check_passed':
                delay_hours = random.uniform(1, 3)  # Quality check: 1-3 hours
            elif status.startswith('shipped'):
                # Calculate shipping time based on distance
                from_loc = manufacturer if 'distribution' in status else distributor
                to_loc = distributor if 'distribution' in status else retailer
                distance = self.calculate_distance(from_loc['location'], to_loc['location'])
                delay_hours = self.calculate_shipping_time(distance) # This returns hours
            elif status.startswith('arrived'):
                delay_hours = random.uniform(2, 6)  # Processing: 2-6 hours
            elif status == 'sold_to_customer':
                delay_hours = random.uniform(1, 2)  # Final sale: 1-2 hours

            # Add issue-related delays if applicable
            if random.random() < 0.2:  # 20% chance of issue
                for issue in self.possible_issues:
                    if random.random() < issue['probability']:
                        min_delay, max_delay = issue['delay']
                        extra_delay = random.uniform(min_delay, max_delay)
                        delay_hours += extra_delay
                        current_issue = issue
                        break

            # Apply the delay to current_date
            current_date += timedelta(hours=delay_hours)

            # Create transaction with the delayed timestamp
            transaction = {
                'product_id': product_id,
                'product_name': product['name'],
                'product_sku': product['sku'],
                'product_category': product['category'],
                'timestamp': current_date.timestamp(),
                'from': self._get_to_party(status, manufacturer, distributor, retailer),
                'to': self._get_to_party(status, manufacturer, distributor, retailer),
                'status': status,
                'location': self._get_location(status, manufacturer, distributor, retailer),
                'additional_data': {
                    'temperature': round(random.uniform(18, 22) + random.uniform(-2, 2), 1) if 'shipped' in status else None,
                    'humidity': round(random.uniform(45, 55), 1) if 'shipped' in status else None,
                    'inspection_id': str(uuid.uuid4()) if 'quality_check' in status else None,
                    'batch_id': f"BATCH-{random.randint(1000, 9999)}",
                }
            }

            # Add issue information if there is one
            if current_issue:
                transaction['additional_data']['issue'] = {
                    'type': current_issue['type'],
                    'description': current_issue['description']
                }
                current_issue = None  # Clear the issue after adding it

            journey.append(transaction)

        return journey
    
    def _get_to_party(self, status, manufacturer, distributor, retailer):
        if status in ['manufactured', 'quality_check_passed']:
            return manufacturer['name']
        elif status in ['shipped_to_distribution', 'arrived_at_distribution']:
            return distributor['name']
        elif status in ['shipped_to_retail', 'arrived_at_retail']:
            return retailer['name']
        else:  # sold_to_customer
            return 'End Customer'

    def _get_location(self, status, manufacturer, distributor, retailer):
        if status in ['manufactured', 'quality_check_passed']:
            return manufacturer['location']
        elif 'distribution' in status:
            return distributor['location'] if 'arrived' in status else self._interpolate_location(
                manufacturer['location'],
                distributor['location'],
                0.5 if 'shipped' in status else 0.9
            )
        elif 'retail' in status:
            return retailer['location'] if 'arrived' in status else self._interpolate_location(
                distributor['location'],
                retailer['location'],
                0.5 if 'shipped' in status else 0.9
            )
        else:  # sold_to_customer
            return retailer['location']

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