import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Enable React fast refresh + JSX transform.
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        // Forward dashboard API calls to local FastAPI server.
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        // Remove "/api" prefix before forwarding.
        rewrite: (path) => path.replace(/^\/api/, "")
      }
    }
  }
});
