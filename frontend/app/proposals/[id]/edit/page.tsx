"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { EditableProposalDetail } from "@/components/proposals/editable-proposal-detail"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Save } from "lucide-react"
import Link from "next/link"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useToast } from "@/hooks/use-toast"

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

  // Simuleer batch informatie (in een echte app zou dit van de API komen)
  const batchInfo = batchId
    ? {
        totalProposals: 42,
        assessedProposals: 11,
        name: "Herverdeling voor week 12 2025",
      }
    : undefined

  const currentProgress = batchInfo ? Math.round((batchInfo.assessedProposals / batchInfo.totalProposals) * 100) : 0
  const progressAfterApproval = batchInfo ? Math.round(((batchInfo.assessedProposals + 1) / batchInfo.totalProposals) * 100) : 0
  const progressIncrease = progressAfterApproval - currentProgress

  // Listen for state changes from EditableProposalDetail
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

  const handleSaveAndApprove = () => {
    // Valideer balans
    if (!isBalanced) {
      toast({
        title: "Ongebalanceerde herverdeling",
        description: "De totale voorraad moet gelijk blijven.",
        variant: "destructive"
      })
      return
    }

    // TODO: Implementeer API call om wijzigingen op te slaan
    // await api.proposals.update(parseInt(params.id), updatedMoves)
    
    // Toon success feedback met groene overlay
    const overlay = document.createElement("div")
    overlay.className = "fixed inset-0 bg-green-500/20 flex items-center justify-center z-50 transition-opacity duration-500"
    overlay.innerHTML = `
      <div class="bg-white dark:bg-gray-800 rounded-full p-6 shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-green-500">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      </div>
    `
    document.body.appendChild(overlay)

    // Update de voortgangsbalk als die bestaat
    if (batchInfo) {
      const progressBar = document.querySelector(".progress-bar-inner") as HTMLElement
      if (progressBar) {
        progressBar.style.transition = "width 0.5s ease-in-out"
        progressBar.style.width = `${progressAfterApproval}%`
      }
    }

    toast({
      title: "Voorstel opgeslagen",
      description: "Het voorstel is succesvol bijgewerkt en goedgekeurd."
    })

    // Wacht kort voor de visuele feedback en navigeer dan
    setTimeout(() => {
      overlay.style.opacity = "0"
      setTimeout(() => {
        document.body.removeChild(overlay)

        // Navigeer naar volgend voorstel of terug
        if (batchId && batchInfo) {
          const nextProposalId = (parseInt(params.id) + 1).toString()
          const hasNextProposal = batchInfo.assessedProposals < batchInfo.totalProposals - 1

          if (hasNextProposal) {
            router.push(`/proposals/${nextProposalId}?batchId=${batchId}`)
          } else {
            router.push(`/proposals/batch/${batchId}`)
          }
        } else {
          router.push(`/proposals/${params.id}`)
        }
      }, 500)
    }, 800)
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
        <DashboardHeader 
          heading={`Voorstel #${params.id} Bewerken`} 
          text="Bewerk de interfiliaalverdeling"
        >
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              onClick={() => router.back()}
            >
              Annuleren
            </Button>
            
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    id="save-button"
                    className="bg-blue-600 hover:bg-blue-700"
                    onClick={handleSaveAndApprove}
                    disabled={!isBalanced || !hasChanges}
                  >
                    <Save className="mr-2 h-4 w-4" />
                    Opslaan & Goedkeuren
                  </Button>
                </TooltipTrigger>
                {(!isBalanced || !hasChanges) && (
                  <TooltipContent>
                    {!isBalanced ? (
                      <p>Ongebalanceerde herverdeling - totale voorraad moet gelijk blijven</p>
                    ) : !hasChanges ? (
                      <p>Geen wijzigingen - maak wijzigingen om op te kunnen slaan</p>
                    ) : null}
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
        batchInfo={batchInfo} 
      />
    </DashboardShell>
  )
}
