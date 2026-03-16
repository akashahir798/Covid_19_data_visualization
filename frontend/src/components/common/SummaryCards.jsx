import { Users, Skull, Heart, Syringe } from 'lucide-react'
import { formatNumber } from '../../services/api'

const SummaryCards = ({ summary }) => {
  if (!summary) return null

  const cards = [
    {
      title: 'Total Cases',
      value: summary.total_confirmed,
      change: summary.new_cases,
      icon: Users,
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      title: 'Total Deaths',
      value: summary.total_deaths,
      change: summary.new_deaths,
      icon: Skull,
      color: 'bg-red-500',
      textColor: 'text-red-600',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
    },
    {
      title: 'Total Recovered',
      value: summary.total_recovered,
      change: summary.new_recovered,
      icon: Heart,
      color: 'bg-green-500',
      textColor: 'text-green-600',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      title: 'Vaccinations',
      value: summary.total_vaccinations,
      change: null,
      icon: Syringe,
      color: 'bg-purple-500',
      textColor: 'text-purple-600',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <div
          key={card.title}
          className="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-slate-700 card-hover"
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <div className="flex items-start justify-between">
            <div className={`p-3 rounded-lg ${card.bgColor}`}>
              <card.icon className={`w-6 h-6 ${card.textColor}`} />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {card.title}
            </p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              {formatNumber(card.value)}
            </p>
            {card.change !== null && (
              <p className={`text-sm mt-2 ${card.change > 0 ? 'text-red-500' : 'text-green-500'}`}>
                {card.change > 0 ? '+' : ''}{formatNumber(card.change)} new cases
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

export default SummaryCards
