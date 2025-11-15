/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        background: "#080808",
        foreground: "#f4f4f5",
        muted: "#1c1c1e",
        card: "#111113",
        border: "#27272a",
      },
    },
  },
  plugins: [],
};
