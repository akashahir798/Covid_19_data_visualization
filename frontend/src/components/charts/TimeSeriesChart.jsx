import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { formatNumber } from '../../services/api'

const TimeSeriesChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
        No data available
      </div>
    )
  }

  // Format data for chart
  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    cases: item.total_confirmed || 0,
    deaths: item.total_deaths || 0,
    recovered: item.total_recovered || 0,
  }))

  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
          <XAxis 
            dataKey="date" 
            stroke="#9ca3af" 
            fontSize={12}
            tickLine={false}
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
            formatter={(value) => formatNumber(value)}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="cases" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={false}
            name="Cases"
          />
          <Line 
            type="monotone" 
            dataKey="deaths" 
            stroke="#ef4444" 
            strokeWidth={2}
            dot={false}
            name="Deaths"
          />
          <Line 
            type="monotone" 
            dataKey="recovered" 
            stroke="#22c55e" 
            strokeWidth={2}
            dot={false}
            name="Recovered"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default TimeSeriesChart
