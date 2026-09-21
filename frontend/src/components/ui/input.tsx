import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = "", ...props }, ref) => {
    return (
      <div className="w-full space-y-1">
        {label && (
          <label className="block text-xs font-black uppercase tracking-wider text-black">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`w-full border-2 border-black rounded-[5px] bg-white px-3 py-2 text-sm font-medium text-black placeholder:text-neutral-400 focus:outline-none focus:shadow-[3px_3px_0px_#000] disabled:bg-neutral-100 disabled:cursor-not-allowed transition-all ${className}`}
          {...props}
        />
        {error && <p className="text-xs font-bold text-red-600 mt-1">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";
