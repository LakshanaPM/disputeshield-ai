import React from 'react';
import ReactDOM from 'react-dom/client';
import axios from 'axios';
import { LicenseManager } from 'ag-grid-enterprise';
import App from './App';
import './index.css';
import './styles/ag-grid-theme.css';

// Configure Axios base URL for Render deployment / production
if (import.meta.env.VITE_API_BASE_URL) {
  axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL;
}

LicenseManager.setLicenseKey(
  import.meta.env.VITE_AG_GRID_LICENSE_KEY || 'YOUR_TRIAL_OR_EVALUATION_KEY'
);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
