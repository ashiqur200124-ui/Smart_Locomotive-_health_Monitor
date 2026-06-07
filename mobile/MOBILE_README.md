# Smart Locomotive Health Monitor - Mobile App

A React Native mobile application for monitoring and analyzing locomotive health in real-time. Built with Expo for cross-platform iOS and Android support.

## Features

✅ **Real-time Dashboard** - View overall locomotive fleet status with critical metrics
✅ **Locomotive Management** - Browse, search, and filter all locomotives
✅ **Health Analysis** - Perform detailed sensor analysis and get AI-driven recommendations
✅ **Alert System** - Real-time alerts filtered by severity level
✅ **Cross-Platform** - Works on iOS, Android, and web
✅ **Offline Support** - Basic functionality works without connection
✅ **Responsive UI** - Optimized for all screen sizes

## Prerequisites

- Node.js 16+ and npm installed
- Expo CLI (`npm install -g expo-cli`)
- Either:
  - iOS development: macOS with Xcode
  - Android development: Android Studio or Android SDK
  - Or use Expo Go app on your phone

## Installation

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Configure Backend URL

Edit `config.js` and update the `API_CONFIG.BASE_URL`:

```javascript
// Development (local)
BASE_URL: 'http://localhost:5000'

// Production
BASE_URL: 'https://your-domain.com'
```

**Note**: For physical devices testing locally, use your machine's IP address instead of `localhost`:
```javascript
BASE_URL: 'http://192.168.x.x:5000'
```

### 3. Start the Backend

Before running the mobile app, ensure the Flask backend is running:

```bash
cd backend
python app.py
# Backend will run on http://localhost:5000
```

## Running the App

### Option 1: Expo CLI (Easiest for Development)

```bash
npm start

# Then press:
# i - for iOS simulator (macOS only)
# a - for Android emulator
# w - for web browser
# j - for development server
```

### Option 2: iOS (macOS Required)

```bash
npm run ios
```

### Option 3: Android

```bash
npm run android
```

### Option 4: Web Browser

```bash
npm run web
```

### Option 5: Physical Device with Expo Go

1. Download Expo Go from App Store or Google Play
2. Run: `npm start`
3. Scan the QR code with your phone's camera
4. App opens in Expo Go

## Project Structure

```
mobile/
├── App.js                      # Main entry point with navigation
├── config.js                   # Configuration and API setup
├── package.json                # Dependencies
├── services/
│   └── api.js                  # Backend API integration
├── screens/
│   ├── DashboardScreen.js      # Fleet overview
│   ├── LocomotiveListScreen.js # Locomotive list and search
│   ├── HealthAnalysisScreen.js # Sensor analysis
│   └── AlertsScreen.js         # System alerts
└── assets/                     # Images and icons
```

## Key Screens

### Dashboard
- Fleet summary with locomotive counts by status
- Total locomotives and average health score
- Recent locomotive activity
- Active alerts count

### Locomotives
- Searchable list of all locomotives
- Filter by status (CRITICAL, WARNING, HEALTHY)
- Tap to view detailed health analysis
- Real-time status indicators

### Health Analysis
- Input sensor readings (temperature, vibration, pressure, etc.)
- AI-powered risk assessment
- Component-specific risk analysis
- Predicted failure times
- Maintenance recommendations

### Alerts
- Centralized alert management
- Filter by severity (CRITICAL, EMERGENCY, WARNING, INFO)
- Detailed alert information
- Recommended actions
- Timestamp tracking

## API Integration

The mobile app connects to the Flask backend API. Key endpoints:

```
GET  /api/locomotives              - Get all locomotives
GET  /api/locomotives/:id          - Get locomotive details
POST /api/health/:id               - Perform health analysis
GET  /api/alerts/:id               - Get locomotive alerts
POST /api/locations/:id            - Get nearby junctions/sheds
GET  /api/summary                  - Dashboard summary
```

### Example API Call

```javascript
import { performHealthAnalysis } from './services/api';

const sensorData = {
  temperature: 85,
  vibration: 5.2,
  pressure: 150,
  oil_quality: 25,
  mileage: 150000,
  latitude: 23.7275,
  longitude: 90.4086
};

const result = await performHealthAnalysis('BR1001', sensorData);
```

## Troubleshooting

### Backend Connection Issues

**Problem**: "Failed to load" errors
**Solution**:
1. Verify backend is running: `curl http://localhost:5000`
2. Check API_BASE_URL in `config.js`
3. For physical devices, use your machine's IP instead of localhost
4. Check firewall settings

### Node Modules Issues

**Problem**: Module not found errors
**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port Conflicts

**Problem**: Port 5000 already in use
**Solution**: Change backend port in `config.js` and restart both apps

### Android Emulator Not Starting

**Problem**: "Could not run gradle"
**Solution**:
```bash
cd android
./gradlew clean
cd ..
npm run android
```

## Development Tips

### Hot Reload
- Changes to JavaScript automatically reload
- Use Ctrl+M (Android) or Cmd+D (iOS) to access dev menu

### Debug Mode
- Use React Native debugger
- Check browser console via web option
- Enable debug in `config.js`: `DEBUG_MODE: true`

### Testing Offline
The app gracefully handles connection loss but features like alerts won't update

## Building for Production

### iOS Build

```bash
eas build --platform ios
# Follow prompts to build for App Store
```

### Android Build

```bash
eas build --platform android
# Creates signed APK for Google Play
```

## Performance Optimization

- Screens use pull-to-refresh for manual updates
- Data caching implemented
- Optimized list rendering with scroll performance
- Lazy loading of locomotive data

## Environment Variables

Create `.env.local` in mobile directory (optional):

```
EXPO_PUBLIC_API_URL=http://your-backend:5000
EXPO_PUBLIC_DEBUG=true
```

Access in code:
```javascript
const apiUrl = process.env.EXPO_PUBLIC_API_URL;
```

## Known Limitations

- Requires active internet connection for most features
- Maps require additional setup (Mapbox/Google Maps)
- Real-time notifications not yet implemented (planned feature)
- Offline data sync not yet implemented

## Future Enhancements

- [ ] Push notifications for critical alerts
- [ ] Offline data sync with SQLite
- [ ] Real-time GPS tracking map
- [ ] Download reports as PDF
- [ ] Voice commands
- [ ] Wearable smartwatch integration
- [ ] Biometric authentication
- [ ] Multiple user roles and permissions

## Dependencies

Key packages:
- `expo` - Cross-platform development framework
- `@react-navigation` - App navigation
- `axios` - HTTP client
- `@expo/vector-icons` - Icon library

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review console logs for error details
3. Check backend connectivity
4. Consult Expo documentation: https://docs.expo.dev

## License

This project is part of Smart Locomotive Health Monitor system.

## 👥 Contributors

- **Lead Developer & Architect**: Ashiqur Rahman
- Full-stack system design, development, and deployment

## 📧 Contact

For questions or support:
- email: support@bangladeshrailway.gov.bd
- phone: +880-2-1234-5678

## Version

**Version**: 2.0.0  
**Last Updated**: June 7, 2026  
**Status**: Production Ready 🚀

---

**Happy monitoring! 🚂**
