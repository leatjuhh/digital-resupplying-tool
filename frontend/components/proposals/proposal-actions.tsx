"use client"

import { DialogFooter } from "@/components/ui/dialog"
import { api } from "@/lib/api"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Check, Download, Edit, Mail, X } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { useToast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface ProposalActionsProps {
  id: string
  batchId?: string
  totalInBatch?: number
  completedInBatch?: number
  nextProposalId?: string
}

export function ProposalActions({
  id,
  batchId,
  totalInBatch = 0,
  completedInBatch = 0,
  nextProposalId,
}: ProposalActionsProps) {
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false)
  const [comment, setComment] = useState("")
  const [reasonCode, setReasonCode] = useState<string>("")
  const [reasonCodes, setReasonCodes] = useState<{ code: string; label: string }[]>([])
  const { toast } = useToast()
  const router = useRouter()

  useEffect(() => {
    api.feedback.getReasonCodes().then((data) => {
      setReasonCodes(data.reason_codes)
    }).catch(() => {/* negeer — dropdown toont dan alleen tekstveld */})
  }, [])

  const currentProgress = totalInBatch > 0 ? Math.round((completedInBatch / totalInBatch) * 100) : 0
  const progressAfterApproval = totalInBatch > 0 ? Math.round(((completedInBatch + 1) / totalInBatch) * 100) : 0
  const progressIncrease = progressAfterApproval - currentProgress

  const handleApprove = async () => {
    try {
      // Call API to approve proposal
      await api.proposals.approve(parseInt(id))
      
      toast({
        title: "Voorstel goedgekeurd",
        description: `Voorstel #${id} is succesvol goedgekeurd.`,
      })
    } catch (error) {
      console.error('Failed to approve proposal:', error)
      toast({
        title: "Fout",
        description: "Kon voorstel niet goedkeuren. Probeer het opnieuw.",
        variant: "destructive",
      })
      return
    }

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
    if (totalInBatch > 0) {
      const progressBar = document.querySelector(".progress-bar-inner") as HTMLElement
      if (progressBar) {
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
          if (nextProposalId) {
            router.push(`/proposals/${nextProposalId}?batchId=${batchId}`)
          } else {
            router.push(`/proposals/batch/${batchId}`)
          }
        } else {
          router.back()
        }
      }, 500) // Wacht tot de fade-out klaar is
    }, 800) // Toon de checkmark voor 800ms
  }

  const handleReject = async () => {
    try {
      // Call API to reject proposal (met optionele reden-code)
      await api.proposals.reject(parseInt(id), comment || undefined, reasonCode || undefined)

      toast({
        title: "Voorstel afgekeurd",
        description: `Voorstel #${id} is afgekeurd.`,
      })

      setRejectDialogOpen(false)
      setComment("")
      setReasonCode("")
      
      // Navigate back or to batch
      if (batchId) {
        router.push(`/proposals/batch/${batchId}`)
      } else {
        router.back()
      }
    } catch (error) {
      console.error('Failed to reject proposal:', error)
      toast({
        title: "Fout",
        description: "Kon voorstel niet afkeuren. Probeer het opnieuw.",
        variant: "destructive",
      })
    }
  }

  const handleEdit = () => {
    router.push(`/proposals/${id}/edit${batchId ? `?batchId=${batchId}` : ""}`)
  }

  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" size="sm">
        <Download className="mr-2 h-4 w-4" />
        Exporteren
      </Button>
      <Button variant="outline" size="sm">
        <Mail className="mr-2 h-4 w-4" />
        Notificatie
      </Button>

      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={handleApprove}>
              <Check className="mr-2 h-4 w-4" />
              Goedkeuren
            </Button>
          </TooltipTrigger>
          {totalInBatch > 0 && (
            <TooltipContent>
              <p>
                Voortgang reeks: {currentProgress}% → {progressAfterApproval}% (+{progressIncrease}%)
              </p>
              <p className="text-xs mt-1">Na goedkeuring wordt het volgende voorstel automatisch geopend</p>
            </TooltipContent>
          )}
        </Tooltip>
      </TooltipProvider>

      <TooltipProvider>
        <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
          <Tooltip>
            <TooltipTrigger asChild>
              <DialogTrigger asChild>
                <Button size="sm" variant="destructive">
                  <X className="mr-2 h-4 w-4" />
                  Afwijzen
                </Button>
              </DialogTrigger>
            </TooltipTrigger>
            {totalInBatch > 0 && (
              <TooltipContent>
                <p>
                  Voortgang reeks: {currentProgress}% → {progressAfterApproval}% (+{progressIncrease}%)
                </p>
              </TooltipContent>
            )}
          </Tooltip>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Voorstel Afwijzen</DialogTitle>
              <DialogDescription>
                Weet u zeker dat u dit voorstel wilt afwijzen? Geef een reden op — dit helpt het model verbeteren.
              </DialogDescription>
            </DialogHeader>
            <div className="py-4 space-y-4">
              {reasonCodes.length > 0 && (
                <div className="space-y-1.5">
                  <Label htmlFor="reason-code">Reden</Label>
                  <select
                    id="reason-code"
                    value={reasonCode}
                    onChange={(e) => setReasonCode(e.target.value)}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Kies reden (optioneel)...</option>
                    {reasonCodes.map((rc) => (
                      <option key={rc.code} value={rc.code}>
                        {rc.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div className="space-y-1.5">
                <Label htmlFor="reject-comment">
                  Toelichting{reasonCode === "other_text" ? " (verplicht)" : " (optioneel)"}
                </Label>
                <Textarea
                  id="reject-comment"
                  placeholder="Aanvullende toelichting..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  className="min-h-[80px]"
                  required={reasonCode === "other_text"}
                />
              </div>
            </div>
            <DialogFooter className="flex flex-col sm:flex-row gap-2">
              <Button variant="outline" onClick={() => setRejectDialogOpen(false)}>
                Annuleren
              </Button>
              <Button onClick={handleReject} variant="destructive">
                Afwijzen
              </Button>
              <Button
                onClick={() => {
                  setRejectDialogOpen(false)
                  handleEdit()
                }}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Edit className="mr-2 h-4 w-4" />
                Afwijzen & Bewerken
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </TooltipProvider>
    </div>
  )
}
