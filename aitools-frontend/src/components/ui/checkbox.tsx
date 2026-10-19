"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, id, ...props }, ref) => (
    <div className="flex items-center gap-2">
      <div className="relative flex items-center">
        <input
          id={id}
          type="checkbox"
          ref={ref}
          className={cn(
            "peer h-4 w-4 appearance-none rounded border border-border bg-card cursor-pointer transition-colors",
            "checked:bg-accent checked:border-accent",
            "focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-50",
            className
          )}
          {...props}
        />
        <svg
          className="pointer-events-none absolute inset-0 hidden h-4 w-4 text-white peer-checked:block"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 16 16"
          fill="currentColor"
        >
          <path d="M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z" />
        </svg>
      </div>
      {label && (
        <label htmlFor={id} className="text-sm text-foreground cursor-pointer select-none">
          {label}
        </label>
      )}
    </div>
  )
);
Checkbox.displayName = "Checkbox";

export { Checkbox };
