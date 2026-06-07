import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: Vite serves the SPA and proxies SSE/api to the Python server (default :8420).
// Prod: the Python server serves the built SPA + SSE from one origin (no proxy, no mixed-content).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/events": { target: "http://127.0.0.1:8420", changeOrigin: true },
      "/api": { target: "http://127.0.0.1:8420", changeOrigin: true },
    },
  },
  build: { outDir: "dist", emptyOutDir: true },
});
