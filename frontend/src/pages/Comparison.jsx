import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { countriesAPI, timeseriesAPI } from '../services/api'
import { formatNumber } from '../services/api'

const Comparison = () => {
  const [countries, setCountries] = useState([])
  const [selectedCountries, setSelectedCountries] = useState(['USA', 'BRA', 'IND'])
  const [comparisonData, setComparisonData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCountries()
  }, [])

  useEffect(() => {
    if (selectedCountries.length > 0) {
      fetchComparisonData()
    }
  }, [selectedCountries])

  const fetchCountries = async () => {
    try {
      const res = await countriesAPI.getCountries('', 20)
      setCountries(res.data?.data || [])
    } catch (err) {
      console.error('Error fetching countries:', err)
    }
  }

  const fetchComparisonData = async () => {
    try {
      setLoading(true)
      const res = await timeseriesAPI.compareCountries(
        selectedCountries.join(','),
        null,
        null,
        'cases'
      )
      setComparisonData(res.data)
    } catch (err) {
      console.error('Error fetching comparison data:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleCountry = (code) => {
    setSelectedCountries(prev => {
      if (prev.includes(code)) {
        return prev.filter(c => c !== code)
      }
      if (prev.length < 5) {
        return [...prev, code]
      }
      return prev
    })
  }

  // Prepare chart data from comparison data
  const chartData = comparisonData?.countries?.map(country => {
    const latestData = country.data?.[country.data.length - 1] || {}
    return {
      name: country.name,
      cases: latestData.value || 0,
    }
  }) || []

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
        Country Comparison
      </h1>

      {/* Country Selector */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Select Countries (max 5)
        </h2>
        <div className="flex flex-wrap gap-2">
          {countries.slice(0, 15).map((country) => (
            <button
              key={country.code}
              onClick={() => toggleCountry(country.code)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCountries.includes(country.code)
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600'
              }`}
            >
              {country.name}
            </button>
          ))}
        </div>
      </div>

      {/* Comparison Chart */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Cases Comparison
        </h2>
        
        {loading ? (
          <div className="flex items-center justify-center h-72">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex items-center justify-center h-72 text-gray-500 dark:text-gray-400">
            Select countries to compare
          </div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                <XAxis 
                  dataKey="name" 
                  stroke="#9ca3af" 
                  fontSize={12}
                  tickLine={false}
                  angle={-45}
                  textAnchor="end"
                  height={80}
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
                <Bar dataKey="cases" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Cases" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Data Table */}
      {comparisonData?.countries && (
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Detailed Comparison
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-slate-700">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">Country</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">Total Cases</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.countries.map((country, index) => {
                  const latestData = country.data?.[country.data.length - 1] || {}
                  return (
                    <tr 
                      key={country.code}
                      className="border-b border-gray-100 dark:border-slate-700"
                    >
                      <td className="py-3 px-4 text-gray-900 dark:text-white font-medium">
                        {country.name}
                      </td>
                      <td className="text-right py-3 px-4 text-gray-900 dark:text-white">
                        {formatNumber(latestData.value || 0)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default Comparison
