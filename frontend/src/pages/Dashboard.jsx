import { useState, useEffect } from 'react'
import { summaryAPI, countriesAPI, timeseriesAPI } from '../services/api'
import SummaryCards from '../components/common/SummaryCards'
import TimeSeriesChart from '../components/charts/TimeSeriesChart'
import TopCountries from '../components/common/TopCountries'
import WorldMap from '../components/map/WorldMap'

const Dashboard = () => {
  const [summary, setSummary] = useState(null)
  const [historicalData, setHistoricalData] = useState([])
  const [topCountries, setTopCountries] = useState([])
  const [mapData, setMapData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch all data in parallel
      const [summaryRes, historicalRes, topRes, mapRes] = await Promise.all([
        summaryAPI.getGlobalSummary(),
        summaryAPI.getHistoricalSummary(30),
        countriesAPI.getTopCountries(10, 'cases'),
        countriesAPI.getMapData(),
      ])

      setSummary(summaryRes.data)
      setHistoricalData(historicalRes.data?.data || [])
      setTopCountries(topRes.data?.data || [])
      setMapData(mapRes.data?.data || [])
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError('Failed to load dashboard data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <p className="text-red-500 text-lg mb-4">{error}</p>
        <button 
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            Global COVID-19 Overview
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Last updated: {summary?.date || 'N/A'}
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <SummaryCards summary={summary} />

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time Series Chart */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Cases Trend (Last 30 Days)
          </h2>
          <TimeSeriesChart data={historicalData} />
        </div>

        {/* Top Countries */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Top 10 Countries by Cases
          </h2>
          <TopCountries countries={topCountries} />
        </div>
      </div>

      {/* World Map */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Global Distribution
        </h2>
        <div className="h-[400px]">
          <WorldMap data={mapData} />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
