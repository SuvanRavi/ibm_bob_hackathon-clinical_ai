/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#faf9f5',
        'surface-soft': '#f5f0e8',
        'surface-card': '#efe9de',
        'surface-cream-strong': '#e8e0d2',
        'surface-dark': '#181715',
        'surface-dark-elevated': '#252320',
        'surface-dark-soft': '#1f1e1b',
        hairline: '#e6dfd8',
        'hairline-soft': '#ebe6df',
        ink: '#141413',
        'body-strong': '#252523',
        body: '#3d3d3a',
        muted: '#6c6a64',
        'muted-soft': '#8e8b82',
        primary: '#cc785c',
        'primary-active': '#a9583e',
        'primary-disabled': '#e6dfd8',
        'on-primary': '#ffffff',
        'on-dark': '#faf9f5',
        'on-dark-soft': '#a09d96',
        'accent-teal': '#5db8a6',
        'accent-amber': '#e8a55a',
        success: '#5db872',
        warning: '#d4a017',
        error: '#c64545',
      },
      fontFamily: {
        display: [
          'Cormorant Garamond',
          'EB Garamond',
          'Garamond',
          'Times New Roman',
          'serif',
        ],
        body: [
          'Inter',
          'Segoe UI',
          'Roboto',
          'system-ui',
          'sans-serif',
        ],
        mono: ['JetBrains Mono', 'Consolas', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        md: '8px',
        lg: '12px',
        xl: '16px',
        pill: '9999px',
      },
      boxShadow: {
        soft: '0 1px 3px rgba(20, 20, 19, 0.08)',
      },
      spacing: {
        section: '96px',
      },
      backgroundImage: {
        'canvas-glow':
          'radial-gradient(1200px 600px at 10% -10%, rgba(204, 120, 92, 0.08), transparent 60%), radial-gradient(900px 500px at 90% 0%, rgba(93, 184, 166, 0.08), transparent 55%)',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-up': 'fadeUp 0.6s ease-out both',
      },
    },
  },
  plugins: [],
}

