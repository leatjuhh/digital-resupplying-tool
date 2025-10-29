"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { BatchDetails } from "@/components/proposals/batch-details"
import { BatchProposalsList } from "@/components/proposals/batch-proposals-list"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Download, Mail } from "lucide-react"
import Link from "next/link"

export default function BatchDetailPage({ params }: { params: { id: string } }) {
  const [batchName, setBatchName] = useState<string>("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchBatchName() {
      try {
        const batchInfo = await api.pdf.getBatchById(parseInt(params.id))
        setBatchName(batchInfo.naam || `Reeks #${params.id}`)
      } catch (error) {
        console.error("Failed to fetch batch name:", error)
        setBatchName(`Reeks #${params.id}`)
      } finally {
        setLoading(false)
      }
    }

    fetchBatchName()
  }, [params.id])

  return (
    <DashboardShell>
      <div className="flex items-center">
        <Button variant="ghost" size="sm" asChild className="mr-4">
          <Link href="/proposals">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Terug
          </Link>
        </Button>
        <DashboardHeader 
          heading={loading ? "Laden..." : batchName} 
          text="Bekijk en beheer alle voorstellen in deze reeks"
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
      </div>
      <BatchDetails id={params.id} />
      <BatchProposalsList id={params.id} />
    </DashboardShell>
  )
}
