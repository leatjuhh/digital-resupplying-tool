import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { ProposalBatches } from "@/components/proposals/proposal-batches"
import { ProposalsFilter } from "@/components/proposals/proposals-filter"
import { Button } from "@/components/ui/button"
import { Download, Mail } from "lucide-react"

export default function ProposalsPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Herverdelingsvoorstellen"
        text="Bekijk en beheer alle herverdelingsvoorstellen per reeks"
      >
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Exporteren
          </Button>
          <Button variant="outline" size="sm">
            <Mail className="mr-2 h-4 w-4" />
            Notificaties
          </Button>
        </div>
      </DashboardHeader>
      <ProposalsFilter />
      <ProposalBatches />
    </DashboardShell>
  )
}
