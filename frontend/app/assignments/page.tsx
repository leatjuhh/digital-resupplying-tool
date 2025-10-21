import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { AssignmentsList } from "@/components/assignments/assignments-list"

export default function AssignmentsPage() {
  return (
    <DashboardShell>
      <DashboardHeader heading="Mijn Opdrachten" text="Bekijk en verwerk de herverdelingsopdrachten voor uw winkel" />
      <AssignmentsList />
    </DashboardShell>
  )
}
