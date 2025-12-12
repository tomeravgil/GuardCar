# Frontend

React-based frontend for the GuardCar vehicle monitoring system.

## Prerequisites
- Node.js 16+ and npm 8+
- Backend server (see backend README for setup)

## Setup

1. Install dependencies:
   ```bash
   cd webapplication
   npm install
   ```

2. Create a `.env` file in the webapplication directory:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_WS_URL=ws://localhost:8000/ws
   ```

## Running

Start the development server:
```bash
cd webapplication
npm start
```

Application will be available at `http://localhost:3000`

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm test`: Launches the test runner
- `npm run build`: Builds the app for production
- `npm run eject`: Ejects from create-react-app (use with caution)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |
| `REACT_APP_WS_URL` | WebSocket URL for real-time updates | `ws://localhost:8000/ws` |

## Project Structure

```
frontend/
├── webapplication/          # Main application code
│   ├── public/              # Static files
│   ├── src/                 # Source files
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── styles/          # Global styles
│   │   └── App.js           # Main application component
│   └── package.json         # Dependencies and scripts
└── README.md               # This file
```

## Testing

Run tests with:
```bash
cd webapplication
npm test
```

## Building for Production

Create an optimized production build:
```bash
cd webapplication
npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Specify your license here]