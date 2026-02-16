import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                medical: {
                    DEFAULT: '#8DF97C',
                    // 40% opacity version pre-calculated if needed, 
                    // or use bg-medical/40 utility
                },
                slate: {
                    850: '#1e293b', // Custom dark shade if needed
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [
        typography,
    ],
}
