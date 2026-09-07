export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#E7E0CB",
        "paper-2": "#DCD3B8",
        ink: "#201C16",
        "ink-soft": "#4A4436",
        teal: "#1F6F6B",
        "teal-deep": "#154C49",
        orange: "#D2571C",
        "orange-deep": "#A5410E",
      },
      fontFamily: {
        display: ["'Bebas Neue'", "sans-serif"],
        body: ["'Space Grotesk'", "sans-serif"],
      },
      boxShadow: {
        stamp: "6px 6px 0 #201C16",
        "stamp-sm": "4px 4px 0 #201C16",
      },
    },
  },
  plugins: [],
};
