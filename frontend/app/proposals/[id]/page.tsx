"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { ProposalDetail } from "@/components/proposals/proposal-detail"
import { ProposalActions } from "@/components/proposals/proposal-actions"
import { Button } from "@/components/ui/button"
import { api, type BatchWithProposals } from "@/lib/api"
import { buildBatchFlowInfo, type BatchFlowInfo } from "@/lib/proposal-flow"

export default function ProposalDetailPage({
  params,
  searchParams,
}: {
  params: { id: string }
  searchParams: { batchId?: string }
}) {
  const batchId = searchParams.batchId
  const [batchFlow, setBatchFlow] = useState<BatchFlowInfo | undefined>(undefined)

  useEffect(() => {
    async function fetchBatchFlow() {
      if (!batchId) {
        setBatchFlow(undefined)
        return
      }

      try {
        const batchData: BatchWithProposals = await api.pdf.getBatchProposals(parseInt(batchId))
        setBatchFlow(buildBatchFlowInfo(batchData.batch_name, batchData.proposals || [], parseInt(params.id)))
      } catch (error) {
        console.error("Failed to fetch batch flow:", error)
        setBatchFlow(undefined)
      }
    }

    fetchBatchFlow()
  }, [batchId, params.id])

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
            totalInBatch={batchFlow?.totalProposals}
            completedInBatch={batchFlow?.assessedProposals}
            nextProposalId={batchFlow?.nextProposalId}
          />
        </DashboardHeader>
      </div>
      <ProposalDetail id={params.id} batchId={batchId} batchInfo={batchFlow} />
    </DashboardShell>
  )
}
