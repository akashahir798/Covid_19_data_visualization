import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { formatNumber } from '../../services/api'

const WorldMap = ({ data }) => {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    // Check if dark mode is active
    const darkMode = document.documentElement.classList.contains('dark')
    setIsDark(darkMode)
    
    // Listen for dark mode changes
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'))
    })
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    })
    
    return () => observer.disconnect()
  }, [])

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
        No map data available
      </div>
    )
  }

  // Get max cases for color scaling
  const maxCases = Math.max(...data.map(d => d.cases))
  
  // Get color based on cases
  const getColor = (cases) => {
    const ratio = cases / maxCases
    if (ratio > 0.5) return '#ef4444' // red
    if (ratio > 0.25) return '#f97316' // orange
    if (ratio > 0.1) return '#eab308' // yellow
    return '#22c55e' // green
  }

  // Map tile URL
  const tileUrl = isDark
    ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

  return (
    <MapContainer
      center={[20, 0]}
      zoom={2}
      scrollWheelZoom={false}
      style={{ height: '100%', width: '100%', borderRadius: '0.5rem' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url={tileUrl}
      />
      {data.map((country) => (
        country.lat && country.lon && (
          <CircleMarker
            key={country.code}
            center={[country.lat, country.lon]}
            radius={Math.max(5, Math.min(20, (country.cases / maxCases) * 20))}
            pathOptions={{
              fillColor: getColor(country.cases),
              fillOpacity: 0.7,
              color: '#fff',
              weight: 1
            }}
          >
            <Popup>
              <div className="text-sm">
                <p className="font-semibold">{country.name}</p>
                <p className="text-gray-600">Cases: {formatNumber(country.cases)}</p>
                <p className="text-gray-600">Deaths: {formatNumber(country.deaths)}</p>
              </div>
            </Popup>
          </CircleMarker>
        )
      ))}
    </MapContainer>
  )
}

export default WorldMap
