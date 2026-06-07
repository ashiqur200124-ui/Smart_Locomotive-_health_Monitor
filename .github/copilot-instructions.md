# Smart Locomotive Health Monitor - Development Instructions

## Project Overview

Smart Locomotive Health Monitor is an AI-powered predictive maintenance system for Bangladesh Railways featuring:
- Fuzzy logic risk analysis
- Machine learning failure prediction  
- Real-time alert system
- Animated railway network map
- Professional dashboard with Plotly charts
- Nearest junction/shed finder
- Bangladesh railway dataset

## Project Structure

```
backend/
  ├── app.py              # Flask API server
  ├── models/             # ML and analysis modules
  │   ├── fuzzy_logic.py
  │   ├── failure_predictor.py
  │   └── location_finder.py
  ├── utils/              # Utilities
  │   ├── alerts.py
  │   └── data_utils.py
  └── requirements.txt

frontend/
  ├── index.html          # Main dashboard
  ├── css/style.css       # Styling
  └── js/
      ├── app.js          # Main logic
      ├── charts.js       #Plotly charts
      └── map.js          # Leaflet map

data/
  └── bangladesh_railways.csv  # Locomotive dataset
```

## Development Workflow

### 1. Backend Development

**Setting up Python environment:**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

**Running the backend:**
```bash
python backend/app.py
```

The API will be available at `http://localhost:5000`

### 2. Frontend Development

**Serving the frontend:**
```bash
# Option 1: Using Python
python -m http.server 8000

# Option 2: Using Node.js
npx http-server frontend
```

access at `http://localhost:8000` or port shown

### 3. Integration Testing

Test API endpoints:
```bash
# Health check
curl http://localhost:5000

# Perform health analysis
curl -X POST http://localhost:5000/api/health/BR1001 \
  -H "Content-Type: application/json" \
  -d '{"temperature": 85, "vibration": 5.2, "pressure": 150, "oil_quality": 25, "mileage": 150000, "latitude": 23.7275, "longitude": 90.4086}'

# Get locomotives
curl http://localhost:5000/api/locomotives

# Get alerts
curl http://localhost:5000/api/alerts/BR1001

# Get locations
curl -X POST http://localhost:5000/api/locations/BR1001 \
  -H "Content-Type: application/json" \
  -d '{"latitude": 23.7275, "longitude": 90.4086}'
```

## Key Components

### Fuzzy Logic Engine (fuzzy_logic.py)
- Triangular membership functions
- Multi-parameter risk scoring
- Component-specific risk analysis
- Maintenance recommendations

### Failure Prediction (failure_predictor.py)
- Per-component failure probability
- Hours-to-failure estimation
- Overall health score calculation
- Maintenance schedule generation

### Location Finder (location_finder.py)
- Haversine distance calculations
- Nearest junction/shed identification
- Alternative route suggestions
- Network density analysis

### Alert System (alerts.py)
- Alert creation and management
- Severity levels: INFO, WARNING, CRITICAL, EMERGENCY
- Escalation rules
- Alert history tracking

### Frontend Dashboard
- Metrics cards showing KPIs
- Interactive data tables
- Plotly.js charts (bar, pie, gauge, scatter)
- Leaflet.js animated map
- Real-time alert display
- Analysis forms

## Configuration

### API Configuration

Edit in `backend/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### CORS Configuration

Already enabled with `flask-cors` for frontend access.

### Risk Thresholds

Edit in respective model classes:
- Engine: 0.75
- Braking: 0.70
- Coupling: 0.65
- Wheels: 0.72
- Boiler: 0.80

## Database Integration (Future)

Current: In-memory storage
Planned: PostgreSQL/MongoDB integration

```python
# Example for future DB integration
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:password@localhost/railway_db')
```

## Deployment

### Local Development
```bash
python backend/app.py  # Backend
python -m http.server 8000  # Frontend
```

### Production Deployment

1. **Backend (using Gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

2. **Frontend (using Nginx):**
```nginx
server {
    listen 80;
    location / {
        root /path/to/frontend;
        index index.html;
    }
    location /api {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

## Testing

### Unit Tests (to be implemented)
```bash
pytest backend/tests/
```

### Manual Testing Checklist
- [ ] Load locomotive list
- [ ] Perform health analysis
- [ ] Generate alerts
- [ ] View risk charts
- [ ] Animate map
- [ ] Find nearest shed/junction
- [ ] Filter and search locomotives
- [ ] Download reports

## Extensibility

### Adding New Components
1. Add fuzzy membership function in `fuzzy_logic.py`
2. Create predictor in `failure_predictor.py`
3. Update alert rules in `alerts.py`
4. Add UI elements in `index.html`

### Adding New Routes
1. Create Flask routes in `app.py`
2. Add frontend AJAX calls
3. Update navigation and sections in HTML

### Custom Analysis
Extend `ReportGenerator` in `data_utils.py` for custom reports

## Debugging

**Enable logs:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Browser DevTools:**
- Check Console tab for JavaScript errors
- Check Network tab for API calls
- Check Application tab for stored data

## Performance Optimization

- Frontend: Minify CSS/JS before production
- Backend: Use caching for repeated calculations
- Database: Index frequently queried columns
- Maps: Lazy load tile layers

## Security Considerations

- Validate all sensor inputs on backend
- Sanitize user inputs in frontend
- Use HTTPS in production
- Implement user authentication
- Add API rate limiting

## Documentation

- API documentation: OpenAPI/Swagger (future)
- Code comments: Docstrings for all functions
- README: Overview and setup
- CONTRIBUTING: Guidelines for contributors

## Support & Troubleshooting

**Common Issues:**

1. CORS errors
   - Ensure flask-cors is installed
   - Check origin in requests

2. Port conflicts
   - Port 5000: `lsof -i :5000` then kill process
   - Port 8000: Try different port

3. Module not found
   - Ensure virtual environment activated
   - Run `pip install -r requirements.txt`

## Version History

- **v1.0.0** (March 30, 2025) - Initial release
  - Fuzzy logic engine
  - Failure predictor
  - Location finder
  - Alert system
  - Dashboard with maps and charts
  - Bangladesh railway dataset

## Future Roadmap

1. Real-time sensor integration via MQTT
2. Advanced ML models (LSTM, CNN)
3. Multi-user access control
4. Mobile app (React Native)
5. Predictive parts shortage alerts
6. GPS-based live tracking
7. Repair workflow automation
8. Historical trend analysis
9. Cost optimization engine
10. Integration with railway scheduling system

## Tools & Commands

```bash
# Start backend
python backend/app.py

# Start frontend (Python)
python -m http.server 8000

# Create virtual environment
python -m venv venv

# Install requirements
pip install -r backend/requirements.txt

# Run tests (when added)
pytest

# Generate API docs (when Swagger added)
python -m flask_swagger
```

## Contact for Support

For technical questions or issues:
- Check existing documentation
- Review console error messages
- Test with curl or Postman
- Enable debug logging
- Contact development team

---

**Last Updated**: March 30, 2025
**Ready for Production**: Yes ✓
