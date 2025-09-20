# Nockpoint Archery Club - Mobile App

This is the mobile companion app for the Nockpoint Archery Club Management System, built with React Native and Expo.

## Features

- **User Authentication**: Secure login with JWT tokens (30-day expiration)
- **Persistent Sessions**: Stay logged in between app launches
- **Upcoming Events**: View and interact with upcoming archery events
- **User Profile**: Display user information and club membership details
- **Cross-Platform**: Works on both iOS and Android

## Technology Stack

- **React Native**: Cross-platform mobile development
- **Expo**: Development platform and toolkit
- **React Navigation**: Navigation between screens
- **React Native Elements**: UI component library
- **Formik & Yup**: Form handling and validation
- **AsyncStorage**: Local data persistence
- **Axios**: HTTP client for API requests

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- Expo Go app on your mobile device (for testing)

### Installation

1. Navigate to the mobile app directory:
```bash
cd mobileapp
```

2. Install dependencies:
```bash
npm install
```

3. Start the Expo development server:
```bash
npm start
```

4. Use the Expo Go app to scan the QR code and run the app on your device

### API Configuration

The app connects to your Flask backend API. Update the API base URL in:
- `src/services/AuthService.js`
- `src/services/ApiService.js`

Change `http://localhost:5000/api` to your production API URL when deploying.

## Project Structure

```
mobileapp/
├── App.js                     # Main app component
├── app.json                   # Expo configuration
├── package.json               # Dependencies and scripts
├── src/
│   ├── components/           # Reusable UI components
│   ├── screens/              # Screen components
│   │   ├── LoginScreen.js    # User authentication
│   │   └── WelcomeScreen.js  # Main dashboard
│   ├── services/             # API and authentication services
│   │   ├── AuthService.js    # Authentication logic
│   │   └── ApiService.js     # API communication
│   ├── navigation/           # Navigation configuration
│   └── utils/                # Utility functions and context
│       └── AuthContext.js    # Authentication state management
└── assets/                   # Images and icons
```

## Authentication Flow

1. **App Launch**: Check for stored JWT token
2. **Token Validation**: Verify token with backend API
3. **Login Screen**: Show if no valid token exists
4. **Welcome Screen**: Display user info and events if authenticated
5. **Auto-Logout**: Clear session if token expires

## Available Scripts

- `npm start` - Start Expo development server
- `npm run android` - Run on Android device/emulator
- `npm run ios` - Run on iOS device/simulator
- `npm run web` - Run in web browser

## API Integration

The app integrates with the following Flask API endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Token validation

### Events
- `GET /api/events` - List events (with filtering)
- `POST /api/events/{id}/register` - Register for event
- `DELETE /api/events/{id}/unregister` - Unregister from event

### Competitions
- `GET /api/competitions` - List competitions
- `POST /api/competitions/{id}/scores` - Submit scores

See `../API_CURL_EXAMPLES.md` for detailed API usage examples.

## Development Notes

- The app uses React Context for authentication state management
- AsyncStorage is used for persistent token storage
- Axios interceptors handle automatic token attachment and logout on 401 errors
- Form validation is handled with Formik and Yup
- UI components use React Native Elements for consistent styling

## Building for Production

### Android
```bash
expo build:android
```

### iOS
```bash
expo build:ios
```

### Standalone Apps
Follow Expo's documentation for building standalone applications for app stores.

## Contributing

1. Create feature branches from `main`
2. Follow React Native and JavaScript best practices
3. Test on both iOS and Android devices
4. Update documentation for new features

## Troubleshooting

### Common Issues

1. **Metro bundler issues**: Clear cache with `expo r -c`
2. **Network errors**: Ensure Flask backend is running and accessible
3. **Token expiration**: App will automatically redirect to login when tokens expire
4. **AsyncStorage errors**: Clear app data or reinstall if persistent storage issues occur

### Development Tips

- Use React Native Debugger for better debugging experience
- Test authentication flow thoroughly on both platforms
- Verify API endpoints work with curl before implementing in app
- Use Expo's built-in debugging tools for network requests