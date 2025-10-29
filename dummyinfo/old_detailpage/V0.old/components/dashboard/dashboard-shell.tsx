import type React from "react"
interface DashboardShellProps {
  children: React.ReactNode
}

export function DashboardShell({ children }: DashboardShellProps) {
  return <div className="flex-1 flex flex-col gap-8 p-4 md:p-8 pt-6">{children}</div>
}
