# src/data_generator/populate_blockchain.py

import requests
import json
import time
from generator import SupplyChainDataGenerator

def populate_blockchain(num_products=5):
    """Populate the blockchain with synthetic supply chain data"""
    
    # Initialize the data generator
    generator = SupplyChainDataGenerator()
    
    # Generate sample data
    transactions = generator.generate_multiple_products(num_products)
    
    # API endpoints
    BASE_URL = "http://localhost:8000"
    
    # Add transactions to blockchain
    for transaction in transactions:
        try:
            # Add transaction
            response = requests.post(
                f"{BASE_URL}/transactions/new",
                json=transaction
            )
            response.raise_for_status()
            print(f"Added transaction for product {transaction['product_id']}")
            
            # Mine block (we'll mine after every transaction for simplicity)
            response = requests.get(f"{BASE_URL}/mine")
            response.raise_for_status()
            print("Mined new block")
            
            # Small delay to prevent overwhelming the server
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error adding transaction: {e}")
            continue

if __name__ == "__main__":
    print("Starting blockchain population...")
    populate_blockchain(5)  # Generate data for 5 products
    print("Finished populating blockchain")