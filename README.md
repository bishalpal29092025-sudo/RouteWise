
# RouteWise — Weather-Aware Route Planning

RouteWise is a weather-aware route planning application that compares alternative driving routes, evaluates weather conditions at route checkpoints, and helps users understand potential travel risks before starting a journey.

The application combines a React and TypeScript frontend with a Django REST API, GraphHopper route data, and Open-Meteo weather forecasts.

## Features

- **Alternative Routes:** Compare multiple routes between an origin and destination.
- **Weather Checkpoints:** Evaluate forecast conditions at selected points along each route.
- **Risk Assessment:** Evaluate wind, rain, snowfall, and configured truck-load risk factors.
- **Safety-Aware Ranking:** Compare routes using evaluated risk and route characteristics.
- **Interactive Map:** Explore route alternatives, checkpoints, risk markers, and weather details.
- **Forecast Timeline:** Navigate checkpoint forecasts using an interactive slider.
- **Risk Visualization:** View color-coded checkpoints and overlays highlighting higher-risk locations.
- **Light and Dark Themes:** Switch between supported visual themes.
- **Backend Health Check:** Check whether the API service is responding.

## Technology Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS v4
- React Leaflet
- Leaflet
- Lucide React
- Motion

### Backend
- Python
- Django
- Django REST Framework
- django-cors-headers
- python-dotenv
- requests

### External Services
- **GraphHopper:** Route calculation and alternative-route data.
- **Open-Meteo:** Weather forecast data.
- **OpenStreetMap:** Map tiles displayed through Leaflet.

## Project Structure

```text
RouteWise/
├── .gitignore
├── README.md
├── backend/
│   ├── .gitignore
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/
│   └── planner/
│       ├── models.py
│       ├── serializers.py
│       ├── urls.py
│       ├── views.py
│       ├── tests.py
│       └── services/
└── frontend/
    ├── .gitignore
    ├── package.json
    ├── package-lock.json
    └── src/
        ├── App.tsx
        ├── App.css
        ├── index.css
        ├── components/
        └── lib/
            └── api.ts
```

## Prerequisites

Install the following before running the application:

- Python compatible with `backend/requirements.txt`
- Node.js and npm compatible with the frontend dependencies
- A GraphHopper API key for route calculation

Check your installed versions:

```bash
python --version
node --version
npm --version
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/bishalpal29092025-sudo/RouteWise.git
cd RouteWise
```

### 2. Set Up the Backend

Create and activate a Python virtual environment from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

Create a `backend/.env` file and add your GraphHopper API key:

```dotenv
GRAPHHOPPER_API_KEY=your_graphhopper_api_key
```

Replace the placeholder with your actual key. Never commit `.env` files or publish API keys.

Ensure that the Django settings and routing service load the key using this environment variable name.

### 3. Run Database Migrations

```bash
cd backend
python manage.py migrate
```

### 4. Start the Backend

From the `backend` directory:

```bash
python manage.py runserver
```

The backend should be available locally at:

`http://127.0.0.1:8000/`

### 5. Set Up the Frontend

Open a second terminal and move to the frontend directory from the project root:

```bash
cd frontend
npm install
```

Create a `frontend/.env` file:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Restart the Vite development server after changing environment variables.

### 6. Start the Frontend

From the `frontend` directory:

```bash
npm run dev
```

Open the local URL printed by Vite, usually:

`http://localhost:5173/`

Keep both the frontend and backend servers running while using the application.

## API Overview

### Health Check

```http
GET /api/health/
```

Checks whether the backend is responding.

### Route Planning

```http
POST /api/route-plan/
Content-Type: application/json
```

Example request:

```json
{
  "origin": "New York, NY",
  "destination": "Chicago, IL",
  "departure_time": "2026-10-14T10:00:00+05:30",
  "truck_load_lbs": "25000"
}
```

Use a departure time appropriate for the intended journey. The exact accepted fields, validation rules, and response format are defined by the backend serializer and route-planning implementation.

The response contains route alternatives, route geometry, checkpoint forecasts, risk assessments, and recommendation information.

## Testing and Production Build

### Backend Tests

From the `backend` directory:

```bash
python manage.py test planner -v 2
```

### Frontend Production Build

From the `frontend` directory:

```bash
npm run build
```

### Frontend Lint

```bash
npm run lint
```

A successful frontend build confirms that TypeScript compilation and Vite bundling complete. Also test the application in the browser and review errors before deployment.

## Security and Deployment

Before deploying:

- Keep API keys and Django secrets in environment variables.
- Never commit `.env` files.
- Set `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` for the deployed backend.
- Restrict CORS to the intended frontend origin.
- Use HTTPS for deployed services.
- Set `VITE_API_BASE_URL` to the deployed API URL.
- Keep virtual environments, local databases, dependency folders, and generated build output out of Git.
- Configure a persistent production database if required.

## Important Limitations

- **Routing Profile:** The current implementation uses a passenger-car routing profile rather than a dedicated truck-routing profile. Truck height, weight, hazardous cargo, and commercial vehicle restrictions are not guaranteed to be considered.
- **Forecast Timing:** Weather forecasts, checkpoint arrival times, and travel durations are estimates and may differ from actual conditions.
- **Checkpoint Visualization:** The translucent risk overlay highlights evaluated high-risk checkpoints. It is not a continuous weather radar or a fully interpolated weather heatmap.
- **Route Accuracy:** Route distances and travel times depend on the routing provider and available road data.
- **Safety Decisions:** RouteWise is a decision-support tool, not a guarantee of road safety. Drivers should consult current official road, weather, and travel advisories.

## Future Improvements

- Integrate dedicated truck routing and vehicle restrictions.
- Improve weather updates and checkpoint forecast handling.
- Add richer route comparison and risk-summary reporting.
- Improve production monitoring, deployment automation, and error reporting.

## License

No license has been specified yet. Unless a license is added, the repository should not be assumed to grant permission to redistribute or reuse its code.
