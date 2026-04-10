import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy /read and /control to the FastAPI backend
    proxy: {
      "/read": "http://127.0.0.1:8000",
      "/control": "http://127.0.0.1:8000",
    },
  },
});