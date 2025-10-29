import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { ProposalDetail } from "@/components/proposals/proposal-detail"
import { ProposalActions } from "@/components/proposals/proposal-actions"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
// Verwijder de useSearchParams import, want die werkt alleen in client components
// import { useSearchParams } from "next/navigation"

// Update de component om de batch informatie door te geven
export default function ProposalDetailPage({
  params,
  searchParams,
}: {
  params: { id: string }
  searchParams: { batchId?: string }
}) {
  // In een echte applicatie zou deze data van een API komen
  // Voor nu simuleren we het met hardcoded data
  const batchId = searchParams.batchId

  // Simuleer batch informatie (in een echte app zou dit van de API komen)
  const batchInfo = batchId
    ? {
        totalProposals: 42,
        assessedProposals: 11, // We nemen aan dat dit voorstel #12 is (0-indexed)
        name: "Herverdeling voor week 12 2025",
      }
    : undefined

  return (
    <DashboardShell>
      <div className="flex items-center">
        <Button variant="ghost" size="sm" asChild className="mr-4">
          <Link href={batchId ? `/proposals/batch/${batchId}` : "/proposals"}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Terug
          </Link>
        </Button>
        <DashboardHeader heading={`Voorstel #${params.id}`} text="Interfiliaalverdeling voorstel">
          <ProposalActions
            id={params.id}
            batchId={batchId}
            totalInBatch={batchInfo?.totalProposals}
            completedInBatch={batchInfo?.assessedProposals}
          />
        </DashboardHeader>
      </div>
      <ProposalDetail id={params.id} batchId={batchId} batchInfo={batchInfo} />
    </DashboardShell>
  )
}
