/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",  // This tells Tailwind to scan these file types
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}