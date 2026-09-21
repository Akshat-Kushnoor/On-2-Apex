import React from "react";

interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
  showLabel?: boolean;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  className = "",
  showLabel = false,
}) => {
  const percentage = Math.min(Math.max(Math.round((value / max) * 100), 0), 100);

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between items-center text-xs font-black mb-1">
          <span>PROGRESS</span>
          <span>{percentage}%</span>
        </div>
      )}
      <div className="w-full h-4 border-2 border-black rounded-[5px] bg-white overflow-hidden p-0.5">
        <div
          className="h-full bg-black transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
