/** @type {import('tailwindcss').Config} */
module.exports = {
  // همه‌ی تمپلیت‌ها و اسکریپت‌هایی که کلاس تیلویند دارند اسکن می‌شوند
  content: [
    './templates/**/*.html',
    './staticfiles/js/dashboard*.js',
    './tailwind/src/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        // نارنجی برند پروژه (#f96747) و طیف آن
        brand: {
          50:  '#fff4f1',
          100: '#ffe7e0',
          200: '#ffcfc3',
          300: '#ffad98',
          400: '#fd866a',
          500: '#f96747',
          600: '#e84c2a',
          700: '#c23b1e',
          800: '#a0331c',
          900: '#842f1c',
        },
      },
      fontFamily: {
        sans: ['Peyda', 'Vazirmatn', 'Tahoma', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgb(15 23 42 / 0.04), 0 4px 16px rgb(15 23 42 / 0.04)',
      },
    },
  },
  plugins: [],
};
