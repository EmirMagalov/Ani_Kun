import axios from "axios";
import { API_BASE_URL } from "@/config"; // у тебя уже должен быть config.js с базовым URL

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Перед каждым запросом добавляем access токен
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Если сервер вернул 401 → пробуем обновить токен
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const { data } = await axios.post(`${API_BASE_URL}/token/refresh/`, {
          refresh: localStorage.getItem("refresh"),
        });
        localStorage.setItem("access", data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return api(originalRequest); // повторяем запрос
      } catch {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        
      }
    }
    return Promise.reject(error);
  }
);

export default api;