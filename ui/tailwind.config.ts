import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0a", // neutral-950
        card: "#171717", // neutral-900
        muted: {
          DEFAULT: "#262626", // neutral-800
          foreground: "#a3a3a3", // neutral-400
        },
        foreground: "#e5e5e5", // neutral-200
        indigo: {
          400: "#818cf8",
          500: "#6366f1",
        },
      },
      borderRadius: {
        '2xl': '1rem',
      },
    },
  },
  plugins: [],
}

export default config
