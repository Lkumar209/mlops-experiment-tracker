import axios from 'axios';

const API_KEY = import.meta.env.VITE_API_KEY || 'dev-api-key';
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.error?.message || error.message || 'Unknown error';
    return Promise.reject(new Error(message));
  }
);

export const sseBaseUrl = `${BASE_URL}/api/v1`;
export const sseApiKey = API_KEY;
