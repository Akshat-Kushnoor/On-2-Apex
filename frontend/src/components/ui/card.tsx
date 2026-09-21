import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ className = "", children, ...props }) => {
  return (
    <div className={`neo-card p-5 ${className}`} {...props}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardProps> = ({ className = "", children, ...props }) => {
  return (
    <div className={`border-b-2 border-black pb-3 mb-4 ${className}`} {...props}>
      {children}
    </div>
  );
};

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  className = "",
  children,
  ...props
}) => {
  return (
    <h3 className={`text-lg font-black tracking-tight text-black ${className}`} {...props}>
      {children}
    </h3>
  );
};

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  className = "",
  children,
  ...props
}) => {
  return (
    <p className={`text-xs text-neutral-600 mt-1 font-medium ${className}`} {...props}>
      {children}
    </p>
  );
};

export const CardContent: React.FC<CardProps> = ({ className = "", children, ...props }) => {
  return (
    <div className={`space-y-3 ${className}`} {...props}>
      {children}
    </div>
  );
};

export const CardFooter: React.FC<CardProps> = ({ className = "", children, ...props }) => {
  return (
    <div className={`border-t-2 border-black pt-3 mt-4 flex items-center justify-between ${className}`} {...props}>
      {children}
    </div>
  );
};
