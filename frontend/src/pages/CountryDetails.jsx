import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Users, Skull, Heart, Syringe } from 'lucide-react'
import { countriesAPI, timeseriesAPI } from '../services/api'
import TimeSeriesChart from '../components/charts/TimeSeriesChart'
import { formatNumber } from '../services/api'

const CountryDetails = () => {
  const { code } = useParams()
  const [country, setCountry] = useState(null)
  const [timeseriesData, setTimeseriesData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [metric, setMetric] = useState('cases')

  useEffect(() => {
    fetchCountryData()
  }, [code, metric])

  const fetchCountryData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [countryRes, timeseriesRes] = await Promise.all([
        countriesAPI.getCountry(code),
        timeseriesAPI.getCountryTimeseries(code, null, null, metric),
      ])

      setCountry(countryRes.data)
      setTimeseriesData(timeseriesRes.data?.data || [])
    } catch (err) {
      console.error('Error fetching country data:', err)
      setError('Failed to load country data. Please try again.')
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
        <Link to="/" className="text-primary-600 hover:underline">
          Return to Dashboard
        </Link>
      </div>
    )
  }

  const stats = country?.statistics || {}

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back Button */}
      <Link
        to="/"
        className="inline-flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
      >
        <ArrowLeft className="mr-2" size={20} />
        Back to Dashboard
      </Link>

      {/* Country Header */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          {country?.name || code}
        </h1>
        <p className="text-gray-500 dark:text-gray-400">
          Last updated: {country?.latest_date || 'N/A'}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Cases</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {formatNumber(stats.confirmed_cases)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <Skull className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Deaths</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {formatNumber(stats.deaths)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <Heart className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Recovered</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {formatNumber(stats.recovered)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <Syringe className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Vaccinated</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {formatNumber(stats.total_vaccinations)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Trend Over Time
          </h2>
          <div className="flex space-x-2 mt-2 sm:mt-0">
            {['cases', 'deaths', 'recovered'].map((m) => (
              <button
                key={m}
                onClick={() => setMetric(m)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  metric === m
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-700'
                }`}
              >
                {m.charAt(0).toUpperCase() + m.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <TimeSeriesChart data={timeseriesData} />
      </div>
    </div>
  )
}

export default CountryDetails
