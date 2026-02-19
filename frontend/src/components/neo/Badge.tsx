/**
 * NeoCampus Badge Component
 * Production-level badge for tags, status indicators, and labels
 */

import React, { forwardRef } from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      children,
      variant = 'secondary',
      size = 'md',
      className = '',
      ...props
    },
    ref
  ) => {
    const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-full transition-colors duration-50';
    
    const variantStyles = {
      primary: 'bg-campus-100 text-campus-700',
      secondary: 'bg-gray-100 text-gray-700',
      success: 'bg-mint-100 text-mint-700',
      warning: 'bg-amber-100 text-amber-700',
      danger: 'bg-coral-100 text-coral-700',
      info: 'bg-blue-100 text-blue-700',
    };
    
    const sizeStyles = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-1 text-xs',
      lg: 'px-3 py-1.5 text-sm',
    };
    
    return (
      <span
        ref={ref}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        {...props}
      >
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

