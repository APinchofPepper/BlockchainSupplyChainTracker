import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { 
  Clock as Timeline,  // Using Clock icon instead of Timeline
  MapPin, 
  Package, 
  Activity, 
  Search 
} from 'lucide-react';

// Rest of the Dashboard component remains the same
const Dashboard = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Fetch products from API
    const fetchProducts = async () => {
      try {
        const response = await fetch('http://localhost:8000/chain');
        const data = await response.json();
        
        // Extract unique products from blockchain transactions
        const uniqueProducts = new Set();
        data.chain.forEach(block => {
          block.transactions.forEach(tx => {
            if (tx.product_id && !uniqueProducts.has(tx.product_id)) {
              uniqueProducts.add(tx.product_id);
            }
          });
        });
        
        setProducts(Array.from(uniqueProducts));
      } catch (error) {
        console.error('Error fetching products:', error);
      }
    };

    fetchProducts();
  }, []);

  const handleProductSelect = async (productId) => {
    try {
      const response = await fetch(`http://localhost:8000/product/${productId}`);
      const data = await response.json();
      setSelectedProduct(data);
    } catch (error) {
      console.error('Error fetching product details:', error);
    }
  };

  const renderTimeline = () => {
    if (!selectedProduct?.history?.length) return null;

    return (
      <div className="p-4 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Timeline className="mr-2" /> Product Journey
        </h3>
        <div className="space-y-4">
          {selectedProduct.history.map((event, index) => (
            <div key={index} className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                <MapPin className="w-4 h-4 text-white" />
              </div>
              <div className="ml-4">
                <p className="font-medium">{event.status.replace(/_/g, ' ').toUpperCase()}</p>
                <p className="text-sm text-gray-500">
                  From: {event.from} → To: {event.to}
                </p>
                <p className="text-sm text-gray-500">
                  {new Date(event.timestamp * 1000).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderMetrics = () => {
    if (!selectedProduct?.history?.length) return null;

    const metrics = selectedProduct.history
      .filter(event => event.additional_data?.temperature)
      .map(event => ({
        time: new Date(event.timestamp * 1000).toLocaleTimeString(),
        temperature: event.additional_data.temperature,
        humidity: event.additional_data.humidity
      }));

    if (!metrics.length) return null;

    return (
      <div className="p-4 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Activity className="mr-2" /> Environmental Metrics
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="temperature"
                stroke="#8884d8"
                name="Temperature (°C)"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="humidity"
                stroke="#82ca9d"
                name="Humidity (%)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2 flex items-center">
          <Package className="mr-2" /> Supply Chain Tracker
        </h2>
        <p className="text-gray-600">
          Track products through their entire supply chain journey
        </p>
      </div>

      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Search products..."
            className="w-full p-2 pl-10 border rounded-lg"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Search className="absolute left-3 top-2.5 text-gray-400" size={20} />
        </div>
        
        <div className="mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {products
            .filter(id => id.includes(searchQuery))
            .map(productId => (
              <button
                key={productId}
                onClick={() => handleProductSelect(productId)}
                className={`p-3 rounded-lg border transition-colors ${
                  selectedProduct?.history?.[0]?.product_id === productId
                    ? 'bg-blue-50 border-blue-500'
                    : 'hover:bg-gray-50'
                }`}
              >
                {productId.slice(0, 8)}...
              </button>
            ))}
        </div>
      </div>

      {selectedProduct && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {renderTimeline()}
          {renderMetrics()}
        </div>
      )}
    </div>
  );
};

export default Dashboard;