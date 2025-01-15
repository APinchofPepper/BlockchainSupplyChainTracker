# Blockchain Supply Chain Tracker

A blockchain-based supply chain tracking system built with Python (FastAPI) and React that provides end-to-end visibility of product movement from manufacturer to end customer.

## Features

- 🔗 Blockchain-based transaction tracking
- 📍 Real-time product location monitoring
- 📊 Environmental metrics tracking (temperature & humidity)
- 🛣️ Product journey visualization
- 🔍 Search functionality
- 📱 Responsive design

## Tech Stack

### Backend
- Python 3.x
- FastAPI
- Custom blockchain implementation
- Synthetic data generation

### Frontend
- React
- Tailwind CSS
- Recharts for data visualization
- Lucide React for icons

## Project Structure

```
blockchain-supply-chain-tracker/
├── src/
│   ├── blockchain/
│   │   └── blockchain.py          # Core blockchain implementation
│   ├── data_generator/
│   │   ├── generator.py           # Synthetic data generator
│   │   └── populate_blockchain.py # Script to populate blockchain
│   └── api/
│       └── main.py                # FastAPI backend
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.jsx      # Main dashboard component
│   │   ├── App.jsx               # Main React application
│   │   ├── index.css             # Global styles
│   │   └── main.jsx              # React entry point
│   ├── package.json              
│   └── vite.config.js            
└── requirements.txt              
```

## Setup & Installation

1. Clone the repository:
```bash
git clone https://github.com/APinchofPepper/BlockchainSupplyTracker.git
cd BlockChainSupplyTracker
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install required packages
pip install fastapi uvicorn python-dotenv web3
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
# From the root directory
source venv/bin/activate
cd src/api
uvicorn main:app --reload
```

2. Populate the blockchain with sample data:
```bash
# In a new terminal
source venv/bin/activate
cd src/data_generator
python populate_blockchain.py
```

3. Start the frontend development server:
```bash
# In a new terminal
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

- `GET /chain` - Get the entire blockchain
- `POST /transactions/new` - Add a new transaction
- `GET /mine` - Mine a new block
- `GET /product/{product_id}` - Get product history

## License

This project is licensed under the MIT License.