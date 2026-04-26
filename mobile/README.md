# Mobile App (Capacitor)

Native Android and iOS wrappers for the 广告思想简史 app using [Capacitor](https://capacitorjs.com/).

## Architecture

The app loads `https://ad-ideas.streamlit.app/` in a native WebView. No separate backend needed.

```
┌─────────────────┐     ┌──────────────────────────┐
│  Android / iOS  │────▶│  Streamlit App (WebView)  │
│  (Capacitor)    │     │  ad-ideas.streamlit.app   │
└─────────────────┘     └──────────────────────────┘
```

## Prerequisites

- **Android**: Android Studio with SDK
- **iOS**: Xcode (macOS only)
- **Node.js** 18+

## Setup

```bash
cd mobile
npm install
npx cap add android   # already done
npx cap add ios       # already done
```

## Development

1. Make changes to the Streamlit app and deploy to Streamlit Cloud
2. Open in Android Studio or Xcode:
   ```bash
   npx cap open android   # Opens Android Studio
   npx cap open ios       # Opens Xcode
   ```
3. The WebView automatically loads the latest version from the Streamlit URL

## Building for Production

### Android

1. Open Android Studio: `npx cap open android`
2. Build → Generate Signed Bundle / APK
3. Or via CLI: `cd android && ./gradlew assembleRelease`

### iOS

1. Open Xcode: `npx cap open ios`
2. Select your development team in Signing & Capabilities
3. Product → Archive → Distribute App

## Configuration

The Streamlit URL is set in `capacitor.config.json`:

```json
"server": {
  "url": "https://ad-ideas.streamlit.app/",
  ...
}
```
