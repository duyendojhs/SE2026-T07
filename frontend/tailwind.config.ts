import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        surface: "var(--surface)",
        "surface-muted": "var(--surface-muted)",
        "surface-subtle": "var(--surface-subtle)",
        secondary: "var(--text-secondary)",
        muted: "var(--text-muted)",
        line: "var(--border)",
        primary: "var(--primary)",
        "primary-soft": "var(--primary-soft)",
        "chart-review": "var(--chart-review)",
        "on-color": "var(--on-color)",
        success: "var(--success)",
        "success-soft": "var(--success-soft)",
        "success-medium": "var(--success-medium)",
        "success-strong": "var(--success-strong)",
        "success-deep": "var(--success-deep)",
        warning: "var(--warning)",
        "warning-soft": "var(--warning-soft)",
        "warning-border": "var(--warning-border)",
        overlay: "rgb(var(--overlay) / <alpha-value>)",
      },
    },
  },
  plugins: [],
};
export default config;
