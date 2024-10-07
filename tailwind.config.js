/** @type {import('tailwindcss').Config} */
const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  content: ["./**/templates/**/*.{html,js,py}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter var", ...defaultTheme.fontFamily.sans],
      },
      width: {
        '85p': '85%',
        '90p': '90%',
        '80p': '80%',
        '1/7': '14.285714285714286%',
        '1/6': '16.666666666666668%',
      }
    },
  },
  plugins: [require("daisyui")],
};
