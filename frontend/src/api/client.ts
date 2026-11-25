
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMsg =
      error.response?.data?.error?.message ||
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred.';

    return Promise.reject(new Error(errorMsg));
  }
);
