"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { ArrowLeft, Save } from "lucide-react"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { EditableProposalDetail } from "@/components/proposals/editable-proposal-detail"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useToast } from "@/hooks/use-toast"
import { api, type BatchWithProposals } from "@/lib/api"
import { buildBatchFlowInfo, buildMovesFromEditableProposal, type BatchFlowInfo } from "@/lib/proposal-flow"

export default function EditProposalPage({
  params,
  searchParams,
}: {
  params: { id: string }
  searchParams: { batchId?: string }
}) {
  const router = useRouter()
  const { toast } = useToast()
  const batchId = searchParams.batchId

  const [isBalanced, setIsBalanced] = useState(true)
  const [hasChanges, setHasChanges] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [proposalData, setProposalData] = useState<any>(null)
  const [batchFlow, setBatchFlow] = useState<BatchFlowInfo | undefined>(undefined)

  useEffect(() => {
    const handleStateChange = (event: CustomEvent) => {
      if (event.detail) {
        setIsBalanced(event.detail.isBalanced)
        setHasChanges(event.detail.hasChanges)
      }
    }

    window.addEventListener("proposalStateChange", handleStateChange as EventListener)
    return () => window.removeEventListener("proposalStateChange", handleStateChange as EventListener)
  }, [])

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

  const handleSaveAndApprove = async () => {
    if (!isBalanced || !proposalData || isSaving) {
      if (!isBalanced) {
        toast({
          title: "Ongebalanceerde herverdeling",
          description: "De totale voorraad moet gelijk blijven.",
          variant: "destructive",
        })
      }
      return
    }

    setIsSaving(true)

    try {
      const updatedMoves = buildMovesFromEditableProposal(proposalData)

      await api.proposals.update(parseInt(params.id), updatedMoves)
      await api.proposals.approve(parseInt(params.id))

      toast({
        title: "Voorstel opgeslagen",
        description: "Het voorstel is bijgewerkt en goedgekeurd.",
      })

      if (batchId) {
        if (batchFlow?.nextProposalId) {
          router.push(`/proposals/${batchFlow.nextProposalId}?batchId=${batchId}`)
        } else {
          router.push(`/proposals/batch/${batchId}`)
        }
        return
      }

      router.push(`/proposals/${params.id}`)
    } catch (error) {
      console.error("Failed to save and approve proposal:", error)
      toast({
        title: "Fout",
        description: "Kon het voorstel niet opslaan en goedkeuren. Probeer het opnieuw.",
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <DashboardShell>
      <div className="flex items-center">
        <Button variant="ghost" size="sm" asChild className="mr-4">
          <Link href={`/proposals/${params.id}${batchId ? `?batchId=${batchId}` : ""}`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Terug naar voorstel
          </Link>
        </Button>
        <DashboardHeader heading={`Voorstel #${params.id} Bewerken`} text="Bewerk de interfiliaalverdeling">
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => router.back()}>
              Annuleren
            </Button>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    id="save-button"
                    className="bg-blue-600 hover:bg-blue-700"
                    onClick={handleSaveAndApprove}
                    disabled={!isBalanced || !hasChanges || isSaving}
                  >
                    <Save className="mr-2 h-4 w-4" />
                    {isSaving ? "Opslaan..." : "Opslaan & Goedkeuren"}
                  </Button>
                </TooltipTrigger>
                {(!isBalanced || !hasChanges) && (
                  <TooltipContent>
                    {!isBalanced ? (
                      <p>Ongebalanceerde herverdeling - totale voorraad moet gelijk blijven</p>
                    ) : (
                      <p>Geen wijzigingen - maak wijzigingen om op te kunnen slaan</p>
                    )}
                  </TooltipContent>
                )}
              </Tooltip>
            </TooltipProvider>
          </div>
        </DashboardHeader>
      </div>
      <EditableProposalDetail
        id={params.id}
        batchId={batchId}
        batchInfo={batchFlow}
        onProposalDataChange={setProposalData}
      />
    </DashboardShell>
  )
}
