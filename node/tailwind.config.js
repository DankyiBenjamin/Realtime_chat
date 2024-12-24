/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // This is the path to the Django template files that will be scanned for Tailwind classes.
    "../templates/**/*.html",
    "../**/templates/**/*.html",
    "../**/forms.py",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
