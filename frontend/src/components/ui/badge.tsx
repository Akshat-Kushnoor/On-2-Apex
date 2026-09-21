import React from "react";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "dark" | "outline" | "highlight";
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = "default",
  className = "",
  children,
  ...props
}) => {
  const base =
    "inline-flex items-center px-2 py-0.5 text-xs font-black uppercase tracking-wider rounded-[5px] border-2 border-black select-none";

  const variants = {
    default: "bg-neutral-100 text-black",
    dark: "bg-black text-white",
    outline: "bg-white text-black",
    highlight: "bg-black text-white shadow-[2px_2px_0px_#000]",
  };

  return (
    <span className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </span>
  );
};
