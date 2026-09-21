import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...props
}) => {
  const baseStyles =
    "neo-btn inline-flex items-center justify-center font-bold tracking-tight disabled:opacity-50 disabled:cursor-not-allowed select-none";

  const variants = {
    primary: "bg-black text-white hover:bg-neutral-900",
    secondary: "bg-white text-black hover:bg-neutral-100",
    danger: "bg-black text-white border-2 border-black hover:bg-red-600",
    ghost: "bg-transparent text-black border-transparent shadow-none hover:bg-neutral-100 hover:border-black",
  };

  const sizes = {
    sm: "text-xs px-2.5 py-1.5",
    md: "text-sm px-4 py-2",
    lg: "text-base px-6 py-3",
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
