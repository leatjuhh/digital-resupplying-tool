"use client"

import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { EditableProposalDetail } from "@/components/proposals/editable-proposal-detail"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useRouter } from "next/navigation"
import { useState, useEffect } from "react"
import { useToast } from "@/hooks/use-toast"

export default function EditProposalPage({
  params,
  searchParams,
}: {
  params: { id: string }
  searchParams: { batchId?: string }
}) {
  const batchId = searchParams.batchId
  const [isBalanced, setIsBalanced] = useState(true)
  const [hasChanges, setHasChanges] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  // Wijzig de handleSaveAndApprove functie om visuele feedback toe te voegen en de voortgangsbalk te animeren

  const handleSaveAndApprove = () => {
    // Toon een tijdelijke overlay met checkmark
    const overlay = document.createElement("div")
    overlay.className =
      "fixed inset-0 bg-green-500/20 flex items-center justify-center z-50 transition-opacity duration-500"
    overlay.innerHTML = `
      <div class="bg-white dark:bg-gray-800 rounded-full p-6 shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" class="text-green-500">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      </div>
    `
    document.body.appendChild(overlay)

    // Update de voortgangsbalk als die bestaat
    if (batchInfo && batchInfo.totalProposals > 0) {
      const progressBar = document.querySelector(".progress-bar-inner") as HTMLElement
      if (progressBar) {
        // Bereken de nieuwe voortgang
        const currentProgress = Math.round((batchInfo.assessedProposals / batchInfo.totalProposals) * 100)
        const progressAfterApproval = Math.round(((batchInfo.assessedProposals + 1) / batchInfo.totalProposals) * 100)

        // Animeer de voortgangsbalk naar de nieuwe waarde
        progressBar.style.transition = "width 0.5s ease-in-out"
        progressBar.style.width = `${progressAfterApproval}%`
      }
    }

    // Wacht kort voor de visuele feedback en navigeer dan
    setTimeout(() => {
      // Verwijder de overlay met fade-out effect
      overlay.style.opacity = "0"
      setTimeout(() => {
        document.body.removeChild(overlay)

        // Navigeer naar het volgende voorstel
        if (batchId) {
          const nextProposalId = (Number.parseInt(params.id) + 1).toString()
          const hasNextProposal = true // Dit zou dynamisch moeten zijn op basis van API data

          if (hasNextProposal) {
            router.push(`/proposals/${nextProposalId}?batchId=${batchId}`)
          } else {
            router.push(`/proposals/batch/${batchId}`)
          }
        } else {
          router.push("/proposals")
        }
      }, 500) // Wacht tot de fade-out klaar is
    }, 800) // Toon de checkmark voor 800ms
  }

  // Effect om de state van de EditableProposalDetail component te synchroniseren
  useEffect(() => {
    const handleStateChange = (event: CustomEvent) => {
      if (event.detail) {
        setIsBalanced(event.detail.isBalanced)
        setHasChanges(event.detail.hasChanges)
      }
    }

    // Luister naar custom events van de EditableProposalDetail component
    window.addEventListener("proposalStateChange", handleStateChange as EventListener)

    return () => {
      window.removeEventListener("proposalStateChange", handleStateChange as EventListener)
    }
  }, [])

  // Simuleer batch informatie (in een echte app zou dit van de API komen)
  const batchInfo = batchId
    ? {
        totalProposals: 42,
        assessedProposals: 11,
        name: "Herverdeling voor week 12 2025",
      }
    : undefined

  // Placeholder values, replace with actual logic
  // const isBalanced = true;
  // const hasChanges = false;

  return (
    <DashboardShell>
      <div className="flex items-center">
        <Button variant="ghost" size="sm" asChild className="mr-4">
          <Link href={`/proposals/${params.id}${batchId ? `?batchId=${batchId}` : ""}`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Terug naar voorstel
          </Link>
        </Button>
        <DashboardHeader heading={`Voorstel #${params.id} bewerken`} text="Pas de voorgestelde herverdeling aan">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link href={`/proposals/${params.id}${batchId ? `?batchId=${batchId}` : ""}`}>Annuleren</Link>
            </Button>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span>
                    <Button
                      size="sm"
                      className="bg-green-600 hover:bg-green-700"
                      id="save-button"
                      disabled={!isBalanced || !hasChanges}
                      onClick={handleSaveAndApprove}
                    >
                      Opslaan & Goedkeuren
                    </Button>
                  </span>
                </TooltipTrigger>
                <TooltipContent side="bottom" align="end" className="max-w-[300px]" hidden={isBalanced && hasChanges}>
                  <div className="text-sm">
                    {!isBalanced ? (
                      <>
                        <p className="font-medium">Ongebalanceerde herverdeling</p>
                        <p>
                          De totale voorraad moet gelijk blijven. Zorg ervoor dat het aantal artikelen dat u toevoegt
                          gelijk is aan het aantal dat u verwijdert.
                        </p>
                      </>
                    ) : !hasChanges ? (
                      <>
                        <p className="font-medium">Geen wijzigingen</p>
                        <p>Maak wijzigingen om op te kunnen slaan.</p>
                      </>
                    ) : null}
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </DashboardHeader>
      </div>
      <EditableProposalDetail id={params.id} batchId={batchId} batchInfo={batchInfo} />
    </DashboardShell>
  )
}
