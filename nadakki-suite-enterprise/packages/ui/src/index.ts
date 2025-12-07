export const Button = ({ children, className, ...props }: any) => (
  <button className={px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition \} {...props}>
    {children}
  </button>
);

export const Card = ({ children, className, ...props }: any) => (
  <div className={g-white rounded-lg shadow p-6 \} {...props}>
    {children}
  </div>
);

export const Badge = ({ children, variant = 'default', className, ...props }: any) => {
  const colors: any = {
    default: 'bg-gray-200 text-gray-800',
    success: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
  };
  return (
    <span className={px-3 py-1 rounded-full text-sm font-medium \ \} {...props}>
      {children}
    </span>
  );
};

export const Input = ({ className, ...props }: any) => (
  <input className={w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 \} {...props} />
);

export const Container = ({ children, className, ...props }: any) => (
  <div className={max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 \} {...props}>
    {children}
  </div>
);
