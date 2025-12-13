
# GuardCar - Frontend Web Application

A modern, responsive Next.js web application for real-time video surveillance, playback, and system management as part of the GuardCar intelligent vehicle security platform.

## Overview

GuardCar is a comprehensive vehicle security and monitoring system that combines:
- **Real-time video streaming** from vehicle cameras
- **AI-powered detection** using YOLO and RF-DETR models
- **Video playback and archival** for incident review
- **Centralized dashboard** for monitoring and configuration

This frontend provides the user interface for accessing live streams, reviewing recordings, and managing system settings.

## Technology Stack

| Component | Version |
|-----------|---------|
| **Framework** | Next.js 15.5.4 |
| **React** | 19.1.0 |
| **Language** | TypeScript |
| **Runtime** | Node.js v22.20.0 |
| **Styling** | Tailwind CSS |
| **Linting** | ESLint |
| **Build Tool** | Turbopack |

## Quick Start

### Prerequisites
- Node.js v22.20.0 or later
- npm, pnpm, or yarn

### Installation & Development

```powershell
# Navigate to the webapp directory
cd frontend/webapplication

# Install dependencies
npm install

# Run the development server (with hot reload)
npm run dev
```

The application will be available at **http://localhost:3000**

**Notes:**
- The project uses Turbopack for faster builds. If unsupported in your environment, remove `--turbopack` from the build scripts in `package.json`
- Alternative package managers: `pnpm install` or `yarn install`

### Production Build

```powershell
# Build the application
npm run build

# Start the production server
npm start
```

## Project Structure

```
webapplication/
├── app/
│   ├── layout.tsx              # Root layout (Shell/Navigation)
│   ├── page.tsx                # Homepage
│   ├── globals.css             # Global styles
│   ├── api/                    # API routes
│   │   └── videos/route.ts     # Video API endpoints
│   ├── components/             # Reusable React components
│   │   ├── sidebar.tsx         # Navigation sidebar
│   │   ├── toast-provider.tsx  # Toast notifications
│   │   └── ui/                 # UI component library
│   ├── live/page.tsx           # Live video streaming page
│   ├── playback/page.tsx       # Video playback & archive page
│   ├── settings/page.tsx       # System configuration page
│   └── login/page.tsx          # Authentication page
├── public/                     # Static assets
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.js          # Tailwind CSS customization
└── eslint.config.mjs           # ESLint rules
```

## Core Pages

### Live Page
Real-time video streaming from connected vehicle cameras.

### ⏯Playback Page
Video review.

### Settings Page
System configuration and administration.

### 🔐 Login Page
User authentication and session management.

## Features

**TypeScript** - Full type safety and developer experience  
**Tailwind CSS** - Utility-first styling framework  
**App Router** - Modern Next.js routing with layouts  
**ESLint** - Code quality enforcement  
**Toast Notifications** - User feedback system  

## Notes

### Environment Variables

Create a `.env.local` file for login:

```env
NEXT_PUBLIC_LOGIN_USER=admin
NEXT_PUBLIC_LOGIN_PASS=1234
```

### Styling Customization
Tailwind configuration is in `tailwind.config.js`. Customize:

### Key Endpoints
- `GET /api/videos` - Fetch available video archives
- `GET /api/cameras` - Get camera list and status
- `POST /api/detection/config` - Update detection settings
- `WS /stream` - WebSocket for live video streaming


### Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React 19 Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
