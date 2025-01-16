import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import {
  Clock,
  MapPin,
  Package,
  Activity,
  Search,
  Truck,
  ThermometerSun,
  Timer,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert
} from 'lucide-react';

export default function SupplyChainDashboard() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [kpiData, setKpiData] = useState(null);
  const [activeTab, setActiveTab] = useState('timeline');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('http://localhost:8000/chain');
        const data = await response.json();
        
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

  const calculateKPIs = (history) => {
    if (!history?.length) return null;

    const temperatures = [];
    let shippingTimes = [];
    let issues = [];

    // Convert Unix timestamps to milliseconds
    const startTime = history[0].timestamp * 1000;
    const endTime = history[history.length - 1].timestamp * 1000;
    const totalTransitTime = (endTime - startTime) / 1000; // Convert back to seconds for display
    
    history.forEach((event, index) => {
      if (event.additional_data?.temperature) {
        temperatures.push(event.additional_data.temperature);
      }
      
      if (event.additional_data?.issue) {
        issues.push(event.additional_data.issue);
      }

      if (event.status.includes('shipped') && index < history.length - 1) {
        const nextEvent = history[index + 1];
        if (nextEvent.status.includes('arrived')) {
          const shippingTime = nextEvent.timestamp - event.timestamp;
          shippingTimes.push(shippingTime);
        }
      }
    });

    const completedStages = new Set(history.map(e => e.status)).size;
    const totalStages = 7; // Total number of stages in the supply chain

    // Format total transit time
    let timeDisplay;
    if (totalTransitTime < 60) {
      timeDisplay = `${totalTransitTime.toFixed(1)}s`;
    } else if (totalTransitTime < 3600) {
      timeDisplay = `${(totalTransitTime / 60).toFixed(1)}m`;
    } else if (totalTransitTime < 86400) {
      timeDisplay = `${(totalTransitTime / 3600).toFixed(1)}h`;
    } else {
      timeDisplay = `${(totalTransitTime / 86400).toFixed(1)}d`;
    }

    return {
      avgDeliveryTime: timeDisplay,
      tempViolations: temperatures.filter(t => t < 18 || t > 22).length,
      totalStops: history.filter(e => e.status.includes('arrived')).length,
      completionRate: ((completedStages / totalStages) * 100).toFixed(1),
      totalIssues: issues.length
    };
  };

  const getStatusIcon = (status, issue) => {
    if (issue) return <AlertTriangle className="w-4 h-4 text-red-500" />;
    switch (status) {
      case 'manufactured':
        return <Package className="w-4 h-4 text-blue-500" />;
      case 'quality_check_passed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'shipped_to_distribution':
      case 'shipped_to_retail':
        return <Truck className="w-4 h-4 text-purple-500" />;
      case 'arrived_at_distribution':
      case 'arrived_at_retail':
        return <MapPin className="w-4 h-4 text-blue-500" />;
      case 'sold_to_customer':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds.toFixed(0)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
    if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
    return `${(seconds / 86400).toFixed(1)}d`;
  };

  const handleProductSelect = async (productId) => {
    try {
      const response = await fetch(`http://localhost:8000/product/${productId}`);
      const data = await response.json();
      setSelectedProduct(data);
      setKpiData(calculateKPIs(data.history));
    } catch (error) {
      console.error('Error fetching product details:', error);
    }
  };

  const renderKPIDashboard = () => {
    if (!kpiData) return null;

    const cards = [
      {
        title: 'Total Time',
        value: kpiData.avgDeliveryTime,
        icon: Timer
      },
      {
        title: 'Temperature Alerts',
        value: kpiData.tempViolations,
        icon: ThermometerSun,
        alert: kpiData.tempViolations > 0
      },
      {
        title: 'Supply Chain Issues',
        value: kpiData.totalIssues,
        icon: ShieldAlert,
        alert: kpiData.totalIssues > 0
      },
      {
        title: 'Completion',
        value: `${kpiData.completionRate}%`,
        icon: Activity
      }
    ];

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {cards.map((card, index) => (
          <div key={index} className={`bg-white rounded-lg shadow p-4 ${
            card.alert ? 'border-l-4 border-red-500' : ''
          }`}>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">{card.title}</h3>
              <card.icon className={`w-4 h-4 ${
                card.alert ? 'text-red-500' : 'text-gray-400'
              }`} />
            </div>
            <div className="text-2xl font-bold text-gray-900">{
              typeof card.value === 'string' && card.value.match(/[hm]$/) ?
                card.value.replace(/([hm])$/, '') :
                card.value
            }{' '}
              <span className="text-base font-medium text-gray-500">
                {typeof card.value === 'string' && card.value.match(/[hm]$/) ?
                  (card.value.endsWith('h') ? 'hours' : 'mins') :
                  ''}
              </span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderTimeline = () => {
    if (!selectedProduct?.history?.length) return null;

    const validHistory = selectedProduct.history
      .filter(event => 
        event && typeof event.timestamp === 'number' && 
        event.status && event.from && event.to
      )
      .sort((a, b) => a.timestamp - b.timestamp); // Ensure chronological order

    if (!validHistory.length) return null;

    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Clock className="mr-2" /> Product Journey
        </h3>
        <div className="space-y-4">
          {validHistory.map((event, index) => {
            const timeDiff = index > 0 ? 
              event.timestamp - validHistory[index - 1].timestamp : 
              0;
              
            return (
              <div key={index} className={`flex items-start ${
                event.additional_data?.issue ? 'bg-red-50 p-4 rounded-lg' : ''
              }`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  event.additional_data?.issue ? 'bg-red-100' : 'bg-blue-500'
                }`}>
                  {getStatusIcon(event.status, event.additional_data?.issue)}
                </div>
                <div className="ml-4 flex-grow">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">{event.status.replace(/_/g, ' ').toUpperCase()}</p>
                    {index > 0 && (
                      <span className="text-sm text-gray-500">
                        +{formatDuration(timeDiff)}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">
                    From: {event.from} → To: {event.to}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(event.timestamp * 1000).toLocaleString()}
                  </p>
                  {event.additional_data?.issue && (
                    <div className="mt-2 p-2 bg-red-100 rounded text-sm text-red-700">
                      <p className="font-semibold">
                        {event.additional_data.issue.type.replace(/_/g, ' ').toUpperCase()}
                      </p>
                      <p>{event.additional_data.issue.description}</p>
                    </div>
                  )}
                  {event.additional_data?.temperature && (
                    <div className={`mt-1 inline-flex items-center px-2 py-1 rounded-full text-xs ${
                      event.additional_data.temperature < 18 || event.additional_data.temperature > 22
                        ? 'bg-red-100 text-red-700'
                        : 'bg-blue-50 text-blue-700'
                    }`}>
                      🌡️ {event.additional_data.temperature}°C | 💧 {event.additional_data.humidity}%
                    </div>
                  )}
                </div>
              </div>
            );
          })}
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
        humidity: event.additional_data.humidity,
        hasIssue: event.additional_data?.issue ? 1 : 0
      }));

    if (!metrics.length) return null;

    return (
      <div className="bg-white rounded-lg shadow p-4">
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
                dot={({ cx, cy, payload }) => {
                  if (!cx || !cy || !payload?.temperature) return null;
                  const isAlert = payload.temperature < 18 || payload.temperature > 22;
                  return isAlert ? (
                    <circle cx={cx} cy={cy} r={4} fill="#EF4444" />
                  ) : (
                    <circle cx={cx} cy={cy} r={3} fill="#8884d8" />
                  );
                }}
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

  // Rest of the component remains the same...
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
            .filter(id => id.toLowerCase().includes(searchQuery.toLowerCase()))
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
        <>
          {renderKPIDashboard()}
          <div className="mb-4">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('timeline')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'timeline'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Metrics
                </button>
              </nav>
            </div>
          </div>

          <div className="mt-4">
            {activeTab === 'timeline' ? renderTimeline() : renderMetrics()}
          </div>
        </>
      )}
    </div>
  );
};