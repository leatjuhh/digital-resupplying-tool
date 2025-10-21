import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { DashboardStats } from "@/components/dashboard/dashboard-stats"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { PendingProposals } from "@/components/dashboard/pending-proposals"
import { NotificationsList } from "@/components/dashboard/notifications-list"
import { PeriodSelector } from "@/components/dashboard/period-selector"

export default function DashboardPage() {
  return (
    <DashboardShell>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <DashboardHeader heading="Dashboard" text="Overzicht van herverdelingsvoorstellen en activiteiten" />
        <PeriodSelector />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <DashboardStats />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <PendingProposals />
        </div>
        <div>
          <RecentActivity />
          <div className="mt-4">
            <NotificationsList />
          </div>
        </div>
      </div>
    </DashboardShell>
  )
}
