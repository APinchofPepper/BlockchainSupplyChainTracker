# src/data_generator/populate_blockchain.py

import requests
import json
import time
from datetime import datetime, timedelta
from generator import SupplyChainDataGenerator

def format_time_difference(start_time, end_time):
    """Format the time difference between two timestamps into a human-readable format"""
    diff = end_time - start_time
    if diff < 60:
        return f"{diff:.1f} seconds"
    elif diff < 3600:
        return f"{diff/60:.1f} minutes"
    else:
        return f"{diff/3600:.1f} hours"

def populate_blockchain(num_products=5):
    """Populate the blockchain with synthetic supply chain data"""
    
    # Initialize the data generator
    generator = SupplyChainDataGenerator()
    
    print(f"\nGenerating supply chain data for {num_products} products...")
    
    # Generate sample data for all products with proper timing
    all_transactions = generator.generate_multiple_products(num_products)
    
    # Sort transactions by timestamp to ensure chronological order
    all_transactions.sort(key=lambda x: x['timestamp'])
    
    # Calculate and display the total time span of the generated data
    if all_transactions:
        start_time = all_transactions[0]['timestamp']
        end_time = all_transactions[-1]['timestamp']
        time_span = format_time_difference(start_time, end_time)
        print(f"Generated {len(all_transactions)} transactions spanning {time_span}")
        print(f"First event: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last event: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # API endpoints
    BASE_URL = "http://localhost:8000"
    
    # Add transactions in batches
    batch_size = 5  # Number of transactions per block
    current_batch = []
    successful_transactions = 0
    failed_transactions = 0
    
    print("\nStarting blockchain population...")
    
    for idx, transaction in enumerate(all_transactions, 1):
        try:
            # Add transaction to current batch
            current_batch.append(transaction)
            
            # When batch is full or it's the last transaction, mine a block
            if len(current_batch) >= batch_size or idx == len(all_transactions):
                # Add all transactions in the batch
                for tx in current_batch:
                    try:
                        response = requests.post(
                            f"{BASE_URL}/transactions/new",
                            json=tx,
                            timeout=5  # Add timeout to prevent hanging
                        )
                        response.raise_for_status()
                        print(f"Added: {tx['product_id']} - {tx['status']} " +
                              f"({datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')})")
                        successful_transactions += 1
                        time.sleep(0.1)  # Small delay between transactions
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to add transaction: {str(e)}")
                        failed_transactions += 1
                        continue
                
                try:
                    # Mine the block
                    response = requests.get(f"{BASE_URL}/mine", timeout=5)
                    response.raise_for_status()
                    print(f"\nMined new block with {len(current_batch)} transactions")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to mine block: {str(e)}")
                    failed_transactions += len(current_batch)
                    successful_transactions -= len(current_batch)
                
                # Clear the batch
                current_batch = []
                
                # Add a small delay between blocks
                time.sleep(0.5)
            
        except Exception as e:
            print(f"Unexpected error processing transaction: {str(e)}")
            failed_transactions += 1
            continue

    # Print summary
    print("\nBlockchain population completed!")
    print(f"Successfully added: {successful_transactions} transactions")
    print(f"Failed to add: {failed_transactions} transactions")
    
    if successful_transactions > 0:
        print("\nSupply chain simulation complete - check the dashboard to view the data!")

if __name__ == "__main__":
    print("Starting blockchain population script...")
    try:
        # Test API connection before starting
        requests.get("http://localhost:8000/", timeout=5)
        populate_blockchain(5)  # Generate data for 5 products
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the blockchain API. Make sure the API server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {str(e)}")