# src/blockchain/blockchain.py

import hashlib
import json
from time import time
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, transactions: List[Dict[str, Any]], 
                 timestamp: float, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the hash of the block using SHA-256"""
        block_string = json.dumps(self.__dict__, sort_keys=True)
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
        self.pending_transactions.append({
            **transaction,
            'timestamp': time()
        })

    def mine_pending_transactions(self) -> Block:
        """Create a new block with pending transactions and add it to the chain"""
        if not self.pending_transactions:
            return None

        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
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
                    history.append({
                        'block_index': block.index,
                        'timestamp': transaction['timestamp'],
                        'from': transaction['from'],
                        'to': transaction['to'],
                        'status': transaction['status'],
                        'location': transaction['location'],
                        'additional_data': transaction.get('additional_data', {})
                    })
        return sorted(history, key=lambda x: x['timestamp'])