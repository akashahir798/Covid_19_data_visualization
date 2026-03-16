import axios from 'axios'

// API base URL - defaults to localhost:8000 in development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.message)
    return Promise.reject(error)
  }
)

// Format large numbers
export const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(2) + 'K'
  }
  return num?.toLocaleString() || '0'
}

// API Endpoints
export const summaryAPI = {
  getGlobalSummary: () => api.get('/summary'),
  getHistoricalSummary: (days = 30) => api.get(`/summary/historical?days=${days}`),
}

export const countriesAPI = {
  getCountries: (search = '', limit = 50) => 
    api.get(`/countries?search=${search}&limit=${limit}`),
  getCountry: (code) => api.get(`/countries/${code}`),
  getTopCountries: (limit = 10, sortBy = 'cases') => 
    api.get(`/top-countries?limit=${limit}&sort_by=${sortBy}`),
  getMapData: () => api.get('/map-data'),
}

export const timeseriesAPI = {
  getCountryTimeseries: (country, startDate, endDate, metric = 'cases') => {
    let url = `/timeseries/${country}?metric=${metric}`
    if (startDate) url += `&start_date=${startDate}`
    if (endDate) url += `&end_date=${endDate}`
    return api.get(url)
  },
  compareCountries: (countries, startDate, endDate, metric = 'cases') => {
    let url = `/timeseries/USA/comparison?countries=${countries}&metric=${metric}`
    if (startDate) url += `&start_date=${startDate}`
    if (endDate) url += `&end_date=${endDate}`
    return api.get(url)
  },
  getGlobalTimeseries: (days = 90, metric = 'cases') => 
    api.get(`/global/timeseries?days=${days}&metric=${metric}`),
}

export const predictionAPI = {
  getPrediction: (country, days = 30) => 
    api.get(`/prediction/${country}?days=${days}`),
  getModelAccuracy: (country) => api.get(`/prediction/${country}/accuracy`),
  getGlobalPredictions: (days = 30) => api.get(`/prediction/global?days=${days}`),
}

export default api
