# COVID-19 Global Data Visualization Dashboard

A comprehensive full-stack data engineering project that visualizes global COVID-19 statistics including cases, deaths, recoveries, vaccination data, and trend predictions.

## 📊 Project Overview

This dashboard provides real-time visualization of global COVID-19 data with predictive analytics capabilities.

### Features
- **Global Summary Cards**: Total cases, deaths, recoveries, vaccination numbers
- **Time Series Charts**: Daily new cases, death trends, recovery trends
- **Geographic Map**: Interactive world map with color-coded severity
- **Country Comparison**: Compare case trends across multiple countries
- **Trend Prediction**: ML-powered 30-day case predictions

## 🛠️ Tech Stack

### Frontend
- React.js 18
- Tailwind CSS 3
- Chart.js / Recharts
- Leaflet.js for maps
- React Router DOM

### Backend
- Python 3.11
- FastAPI
- Pandas
- NumPy
- Scikit-learn

### Database
- SQLite (for development)
- PostgreSQL (production ready)

### DevOps
- Docker & Docker Compose

## 📁 Project Structure

```
covid-dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── summary.py        # Global summary endpoint
│   │   │   ├── countries.py      # Country endpoints
│   │   │   ├── timeseries.py     # Time series endpoints
│   │   │   └── prediction.py     # Prediction endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_service.py   # Data processing
│   │   │   └── ml_service.py     # ML predictions
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py        # Utility functions
│   ├── data/
│   │   ├── raw/                  # Raw COVID data
│   │   └── processed/            # Processed data
│   ├── models/                   # Saved ML models
│   ├── scripts/
│   │   ├── fetch_data.py         # Data fetching script
│   │   ├── preprocess_data.py    # Data preprocessing
│   │   └── train_model.py        # Model training
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── charts/
│   │   │   ├── map/
│   │   │   └── layout/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

### Option 1: Docker (Recommended)

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Run with Docker Compose:

```bash
# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📡 API Endpoints

### Global Summary
```
GET /api/v1/summary
```
Returns global COVID-19 statistics.

### Country Data
```
GET /api/v1/countries
GET /api/v1/countries/{country_code}
```

### Time Series
```
GET /api/v1/timeseries/{country}
GET /api/v1/timeseries/{country}?start_date=2023-01-01&end_date=2023-12-31
```

### Top Countries
```
GET /api/v1/top-countries?limit=10&sort_by=cases
```

### Predictions
```
GET /api/v1/prediction/{country}?days=30
```

## 🔧 Environment Variables

```env
# Backend
DATABASE_URL=sqlite:///./covid_data.db
API_KEY=your_api_key_here
LOG_LEVEL=INFO

# Frontend
VITE_API_URL=http://localhost:8000
VITE_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## 🚀 Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
c cd covid-dashboard

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Option 2: Manual Deployment

#### Backend (Render/Railway/AWS EC2)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:pass@host:5432/coviddb
export API_KEY=your_api_key

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend (Vercel/Netlify)

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Deploy to Vercel
npm i -g vercel
vercel --prod
```

### Option 3: Production Docker

```bash
# Build production images
docker build -t covid-backend ./backend
docker build -t covid-frontend ./frontend

# Run containers
docker run -d -p 8000:8000 --env-file .env covid-backend
docker run -d -p 3000:3000 -e VITE_API_URL=https://your-backend.com covid-frontend
```

### Environment Variables for Production

```env
# Backend
DATABASE_URL=postgresql://user:password@host:5432/coviddb
API_KEY=your_secure_api_key
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend.vercel.app

# Frontend
VITE_API_URL=https://your-backend.onrender.com
```

### Deployment Platforms

| Platform | Backend | Frontend |
|----------|---------|----------|
| Render | ✅ Native support | ✅ Native support |
| Railway | ✅ Native support | ✅ Native support |
| AWS EC2 | ✅ Docker | ✅ Docker |
| Vercel | ❌ | ✅ Native support |
| Netlify | ❌ | ✅ Native support |

### Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose up backend
```

## 🧪 Features in Detail

### 1. Data Pipeline
- Automatically fetches COVID-19 data from public APIs
- Cleans and preprocesses the dataset
- Stores processed data in SQLite/PostgreSQL

### 2. Interactive Dashboard
- Dark/Light mode toggle
- Country dropdown selector
- Date range filter
- Search functionality
- Real-time data updates

### 3. Visualizations
- **Line Charts**: Time series trends
- **Bar Charts**: Country comparisons
- **Pie Charts**: Case distribution
- **World Map**: Geographic case distribution

### 4. ML Predictions
- Linear Regression model for trend prediction
- 30-day forecast capability
- Confidence intervals

## 📦 Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose up backend
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Johns Hopkins University COVID-19 Data
- Our World in Data
- World Health Organization (WHO)

---

Built with ❤️ using React, FastAPI, and Machine Learning
