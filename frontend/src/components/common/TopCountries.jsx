import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { formatNumber } from '../../services/api'

const TopCountries = ({ countries }) => {
  if (!countries || countries.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
        No data available
      </div>
    )
  }

  // Get max cases for percentage bar
  const maxCases = Math.max(...countries.map(c => c.total_cases))

  return (
    <div className="space-y-3 max-h-72 overflow-y-auto">
      {countries.map((country, index) => (
        <Link
          key={country.code}
          to={`/country/${country.code}`}
          className="block p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-500 dark:text-gray-400 w-6">
                #{index + 1}
              </span>
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  {country.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {country.code}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                {formatNumber(country.total_cases)}
              </span>
              <ArrowRight size={16} className="text-gray-400" />
            </div>
          </div>
          {/* Progress bar */}
          <div className="mt-2 w-full bg-gray-200 dark:bg-slate-600 rounded-full h-2">
            <div
              className="bg-primary-500 h-2 rounded-full"
              style={{ width: `${(country.total_cases / maxCases) * 100}%` }}
            />
          </div>
        </Link>
      ))}
    </div>
  )
}

export default TopCountries
