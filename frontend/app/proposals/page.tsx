import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { ExternalAlgorithmStatus } from "@/components/proposals/external-algorithm-status"
import { ProposalBatches } from "@/components/proposals/proposal-batches"

export default function ProposalsPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Herverdelingsvoorstellen"
        text="Bekijk en beheer alle herverdelingsvoorstellen per reeks"
      />
      <ExternalAlgorithmStatus />
      <ProposalBatches />
    </DashboardShell>
  )
}
