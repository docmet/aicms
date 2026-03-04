import * as React from "react"
import { cn } from "@/lib/utils"

export interface CodeProps extends React.HTMLAttributes<HTMLElement> {
  variant?: "default" | "muted"
}

const Code = React.forwardRef<HTMLElement, CodeProps>(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <code
        ref={ref}
        className={cn(
          "relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm",
          variant === "muted" && "text-muted-foreground",
          className
        )}
        {...props}
      />
    )
  }
)
Code.displayName = "Code"

export { Code }
