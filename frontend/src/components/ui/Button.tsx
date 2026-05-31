import React from 'react';

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'ghost';
  icon?: React.ReactNode;
};

export default function Button({ variant = 'primary', icon, children, ...rest }: ButtonProps) {
  const cls = variant === 'ghost' ? 'btn-ghost' : 'btn-primary';
  return (
    <button className={`${cls}`} {...rest}>
      {icon && <span className="opacity-90">{icon}</span>}
      <span>{children}</span>
    </button>
  );
}
