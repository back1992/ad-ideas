# Mobile App (Capacitor)

Native Android and iOS wrappers for the 广告思想简史 app using [Capacitor](https://capacitorjs.com/).

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Android / iOS  │────▶│  Mobile Web UI   │────▶│  FastAPI    │
│  (Capacitor)    │     │  (HTML/CSS/JS)   │     │  Backend    │
└─────────────────┘     └──────────────────┘     └─────────────┘
                                                Uses same SQLite DB
```

## Prerequisites

- **Android**: Android Studio with SDK, or run `npx cap open android`
- **iOS**: Xcode (macOS only), or run `npx cap open ios`
- **Node.js** 18+

## Setup (already done)

```bash
cd mobile
npm install
npx cap add android
npx cap add ios
```

## Development

1. Update web files in `mobile/www/` (HTML, CSS, JS)
2. Sync changes to native projects:
   ```bash
   npx cap sync
   ```
3. Open in Android Studio or Xcode:
   ```bash
   npx cap open android   # Opens Android Studio
   npx cap open ios       # Opens Xcode
   ```

## Building for Production

### Android

1. Open Android Studio: `npx cap open android`
2. Build → Generate Signed Bundle / APK
3. Or via CLI: `cd android && ./gradlew assembleRelease`

### iOS

1. Open Xcode: `npx cap open ios`
2. Select your development team in Signing & Capabilities
3. Product → Archive → Distribute App

## API Configuration

The mobile app communicates with the FastAPI backend. Set `API_BASE` in `www/js/app.js`:

- **Development**: `const API_BASE = 'http://localhost:8000';`
- **Production**: `const API_BASE = '';` (same origin, proxied)

## Starting the API

```bash
cd /home/ubuntu/TupProjects/ad-ideas
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
