import React from 'react';

type CardProps = React.PropsWithChildren<{
  title?: string;
  subtitle?: string;
  className?: string;
}>;

export default function Card({ title, subtitle, children, className = '' }: CardProps) {
  return (
    <div className={`card ${className}`}>
      {title && (
        <div className="mb-3">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          {subtitle && <p className="text-slate-400 text-sm mt-1">{subtitle}</p>}
        </div>
      )}
      <div className="mt-2">{children}</div>
    </div>
  );
}
