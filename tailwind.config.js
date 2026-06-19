/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        film: {
          dark: '#1a1a1a',
          yellow: '#f5c542',
          cream: '#faf8f5',
          red: '#c44536',
          green: '#4a5d23',
          brown: '#3d2b1f',
        }
      },
      fontFamily: {
        display: ['Playfair Display', 'serif'],
        body: ['Source Sans 3', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
