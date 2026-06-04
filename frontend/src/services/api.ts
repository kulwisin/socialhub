import axios from "axios";
import { env } from "@/lib/env";

export const api = axios.create({
  baseURL: `${env.API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail =
      error.response?.data?.detail ?? error.message ?? "Something went wrong";
    return Promise.reject(new Error(detail));
  }
);
