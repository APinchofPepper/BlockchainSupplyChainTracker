import hashlib
import json
from time import time
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, transactions: List[Dict[str, Any]], 
                 timestamp: float, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp  # Block creation timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the hash of the block using SHA-256"""
        # Create a copy of the dict without the hash
        block_dict = self.__dict__.copy()
        block_dict.pop('hash', None)
        block_string = json.dumps(block_dict, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class SupplyChainBlockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Create the initial block in the chain"""
        genesis_block = Block(0, [], time(), "0")
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Return the most recent block in the chain"""
        return self.chain[-1]

    def add_transaction(self, transaction: Dict[str, Any]) -> None:
        """Add a new transaction to pending transactions"""
        # Preserve the original transaction data without modification
        self.pending_transactions.append(transaction.copy())

    def mine_pending_transactions(self) -> Block:
        """Create a new block with pending transactions and add it to the chain"""
        if not self.pending_transactions:
            return None

        # Create new block with current timestamp but preserve transaction timestamps
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),  # Make a copy to prevent modifications
            timestamp=time(),
            previous_hash=self.get_latest_block().hash
        )

        # Simple proof of work
        while not new_block.hash.startswith('00'):  # Simplified difficulty
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def get_product_history(self, product_id: str) -> List[Dict[str, Any]]:
        """Get the complete transaction history for a specific product"""
        history = []
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get('product_id') == product_id:
                    # Create a deep copy of the transaction to prevent modifications
                    tx_copy = json.loads(json.dumps(transaction))
                    history.append({
                        'block_index': block.index,
                        'timestamp': tx_copy['timestamp'],
                        'from': tx_copy['from'],
                        'to': tx_copy['to'],
                        'status': tx_copy['status'],
                        'location': tx_copy.get('location', {}),
                        'additional_data': tx_copy.get('additional_data', {}),
                        'product_id': tx_copy.get('product_id'),
                        'product_name': tx_copy.get('product_name'),
                        'product_sku': tx_copy.get('product_sku'),
                        'product_category': tx_copy.get('product_category')
                    })
        
        # Sort by timestamp and ensure data integrity
        return sorted(history, key=lambda x: x['timestamp'])