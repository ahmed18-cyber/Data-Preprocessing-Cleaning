/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: '#FAF5E6',
        black: '#000000',
        orange: '#FF4400',
        cobalt: '#0047AB',
        slate: {
          850: '#151e2e',
          950: '#0a0f1d',
        },
      },
    },
  },
  plugins: [],
}

