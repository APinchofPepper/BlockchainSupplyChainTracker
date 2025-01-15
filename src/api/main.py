# src/api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.blockchain.blockchain import SupplyChainBlockchain

app = FastAPI(title="Supply Chain Blockchain API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize blockchain
blockchain = SupplyChainBlockchain()

@app.get("/")
async def read_root():
    return {"message": "Supply Chain Blockchain API"}

@app.post("/transactions/new")
async def new_transaction(transaction: Dict[str, Any]):
    """Add a new transaction to the blockchain"""
    try:
        blockchain.add_transaction(transaction)
        return {"message": "Transaction added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mine")
async def mine():
    """Mine a new block"""
    block = blockchain.mine_pending_transactions()
    if block is None:
        raise HTTPException(status_code=400, detail="No pending transactions to mine")
    return {
        "message": "New block mined",
        "block_index": block.index,
        "transactions": block.transactions,
    }

@app.get("/product/{product_id}")
async def get_product_history(product_id: str):
    """Get the complete history of a product"""
    history = blockchain.get_product_history(product_id)
    return {"history": history}

@app.get("/chain")
async def get_chain():
    """Get the entire blockchain"""
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "previous_hash": block.previous_hash,
            "hash": block.hash
        })
    return {"chain": chain_data, "length": len(chain_data)}