import axios from "axios";

// Base API configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://ai-scraper-at0b.onrender.com/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach JWT token from localStorage to requests
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercept responses for auth errors (e.g. expired tokens)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (typeof window !== "undefined" && error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("email");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
