// src/components/common/Button/Button.jsx
export default function Button({ children, variant = 'primary', ...props }) {
  const baseClasses = 'px-4 py-2 rounded-lg font-semibold transition-colors';
  const variants = {
    primary: 'bg-primary text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-danger text-white hover:bg-red-600',
  };
  
  return (
    <button 
      className={`${baseClasses} ${variants[variant]}`}
      {...props}
    >
      {children}
    </button>
  );
}