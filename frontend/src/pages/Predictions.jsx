import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts'
import { predictionAPI, countriesAPI } from '../services/api'
import { formatNumber } from '../services/api'

const Predictions = () => {
  const [countries, setCountries] = useState([])
  const [selectedCountry, setSelectedCountry] = useState('USA')
  const [predictionDays, setPredictionDays] = useState(30)
  const [predictionData, setPredictionData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchCountries()
  }, [])

  useEffect(() => {
    fetchPredictions()
  }, [selectedCountry, predictionDays])

  const fetchCountries = async () => {
    try {
      const res = await countriesAPI.getCountries('', 20)
      setCountries(res.data?.data || [])
    } catch (err) {
      console.error('Error fetching countries:', err)
    }
  }

  const fetchPredictions = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const res = await predictionAPI.getPrediction(selectedCountry, predictionDays)
      setPredictionData(res.data)
    } catch (err) {
      console.error('Error fetching predictions:', err)
      setError('Failed to load predictions. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data
  const chartData = () => {
    if (!predictionData) return []
    
    const historical = predictionData.historical_data?.map(d => ({
      date: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      actual: d.cases,
      predicted: null,
      lower: null,
      upper: null,
    })) || []
    
    const predictions = predictionData.predictions?.map(d => ({
      date: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      actual: null,
      predicted: d.predicted_cases,
      lower: d.lower_bound,
      upper: d.upper_bound,
    })) || []
    
    // Get last historical point for connecting line
    const lastHistorical = historical[historical.length - 1]
    if (lastHistorical && predictions.length > 0) {
      predictions.unshift({
        date: lastHistorical.date,
        actual: null,
        predicted: lastHistorical.actual,
        lower: lastHistorical.actual,
        upper: lastHistorical.actual,
      })
    }
    
    return [...historical, ...predictions]
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
        COVID-19 Predictions
      </h1>

      {/* Country Selector */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Country
            </label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            >
              {countries.map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="w-full sm:w-48">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Prediction Days
            </label>
            <select
              value={predictionDays}
              onChange={(e) => setPredictionDays(Number(e.target.value))}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
            >
              <option value={7}>7 Days</option>
              <option value={14}>14 Days</option>
              <option value={30}>30 Days</option>
              <option value={60}>60 Days</option>
              <option value={90}>90 Days</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <p className="text-red-500 text-lg mb-4">{error}</p>
          <button 
            onClick={fetchPredictions}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Retry
          </button>
        </div>
      ) : (
        <>
          {/* Prediction Chart */}
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {predictionData?.country} - {predictionDays} Day Prediction
            </h2>
            
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData()} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                  <XAxis 
                    dataKey="date" 
                    stroke="#9ca3af" 
                    fontSize={10}
                    tickLine={false}
                    interval="preserveStartEnd"
                  />
                  <YAxis 
                    stroke="#9ca3af" 
                    fontSize={12}
                    tickFormatter={(value) => formatNumber(value)}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                    formatter={(value) => value ? formatNumber(value) : 'N/A'}
                  />
                  <Legend />
                  
                  {/* Confidence interval area */}
                  <Area 
                    type="monotone" 
                    dataKey="upper" 
                    stroke="transparent"
                    fill="#3b82f6"
                    fillOpacity={0.1}
                    name="Upper Bound"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="lower" 
                    stroke="transparent"
                    fill="#1f2937"
                    fillOpacity={1}
                    name="Lower Bound"
                  />
                  
                  {/* Historical data line */}
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={false}
                    name="Historical Cases"
                    connectNulls
                  />
                  
                  {/* Prediction line */}
                  <Line 
                    type="monotone" 
                    dataKey="predicted" 
                    stroke="#f97316" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    name="Predicted Cases"
                    connectNulls
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Prediction Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
              <p className="text-sm text-gray-500 dark:text-gray-400">Current Cases</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatNumber(predictionData?.historical_data?.[predictionData.historical_data.length - 1]?.cases || 0)}
              </p>
            </div>
            
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
              <p className="text-sm text-gray-500 dark:text-gray-400">Predicted Cases ({predictionDays} days)</p>
              <p className="text-2xl font-bold text-orange-500">
                {formatNumber(predictionData?.predictions?.[predictionData.predictions.length - 1]?.predicted_cases || 0)}
              </p>
            </div>
            
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
              <p className="text-sm text-gray-500 dark:text-gray-400">Model</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {predictionData?.model_info?.type || 'Linear Regression'}
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Predictions
