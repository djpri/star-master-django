import { defineConfig } from "vite";
import { resolve } from "path";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],

  // Entry points for your assets
  build: {
    // Output to Django's static directory
    outDir: "static/dist",
    emptyOutDir: true,
    manifest: "assets/manifest.json", // Move manifest to assets directory
    rollupOptions: {
      input: {
        main: resolve(__dirname, "static/js/main.js"),
        style: resolve(__dirname, "static/css/input.css"),
      },
      output: {
        assetFileNames: "assets/[name].[hash].[ext]",
      },
    },
  },
  // Development server configuration
  server: {
    host: "localhost",
    port: 5173,
    open: false,
    watch: {
      usePolling: true,
      interval: 1000,
    },
    cors: true,
  },
});
