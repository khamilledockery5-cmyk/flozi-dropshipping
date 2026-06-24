import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f14",
        panel: "#121821",
        accent: "#3b82f6",
        up: "#22c55e",
        down: "#ef4444",
      },
    },
  },
  plugins: [],
};

export default config;
