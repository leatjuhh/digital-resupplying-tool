import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { AssignmentsList } from "@/components/assignments/assignments-list"
import { FeatureStatusBanner } from "@/components/ui/feature-status-banner"

export default function AssignmentsPage() {
  return (
    <DashboardShell>
      <DashboardHeader heading="Mijn Opdrachten" text="Bekijk en verwerk de herverdelingsopdrachten voor uw winkel" />
      <FeatureStatusBanner description="Deze assignments-flow draait nu op echte proposaldata en statusupdates, maar hoort tijdens de consolidatie nog steeds niet bij de leidende productkern." />
      <AssignmentsList />
    </DashboardShell>
  )
}
