"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface BatchDetailsProps {
  id: string
}

export function BatchDetails({ id }: BatchDetailsProps) {
  const [batchData, setBatchData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch batch data from API
  useEffect(() => {
    async function fetchBatchData() {
      try {
        setLoading(true)
        
        // Fetch batch info and proposals
        const [batchInfo, proposalsData] = await Promise.all([
          api.pdf.getBatchById(parseInt(id)),
          api.pdf.getBatchProposals(parseInt(id))
        ])
        
        // Format date
        const date = new Date(batchInfo.created_at)
        const formattedDate = date.toLocaleDateString('nl-NL', { 
          day: 'numeric', 
          month: 'long', 
          year: 'numeric' 
        })
        
        setBatchData({
          id,
          description: batchInfo.naam || `Batch ${id}`,
          date: formattedDate,
          count: proposalsData.total_proposals || 0,
          approved: proposalsData.status_counts?.approved || 0,
          rejected: proposalsData.status_counts?.rejected || 0,
          pending: proposalsData.status_counts?.pending || 0,
          edited: proposalsData.status_counts?.edited || 0,
          generatedBy: "Systeem",
          collection: batchInfo.naam || "Onbekend",
          type: "auto",
        })
        setError(null)
      } catch (err) {
        console.error('Failed to fetch batch data:', err)
        setError('Kon batch details niet ophalen')
      } finally {
        setLoading(false)
      }
    }

    fetchBatchData()
  }, [id])

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 my-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Laden...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !batchData) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 my-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">{error || 'Geen data beschikbaar'}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const progressPercentage = batchData.count > 0 
    ? Math.round(((batchData.approved + batchData.rejected) / batchData.count) * 100)
    : 0

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 my-6">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm">
            <p className="font-medium">{batchData.description}</p>
            <p className="text-muted-foreground mt-1">Aangemaakt: {batchData.date}</p>
            <p className="text-muted-foreground">Door: {batchData.generatedBy}</p>
            <p className="text-muted-foreground">Collectie: {batchData.collection}</p>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Voortgang</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between text-2xl">
              <span className="font-bold">{progressPercentage}%</span>
              <Badge variant={progressPercentage === 100 ? "default" : "outline"}>
                {progressPercentage === 100 ? "Voltooid" : "In behandeling"}
              </Badge>
            </div>
            <div className="h-2 w-full rounded-full bg-secondary">
              <div
                className={`h-full rounded-full ${progressPercentage === 100 ? "bg-green-500" : "bg-blue-500"}`}
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
            <div className="grid grid-cols-3 gap-2 text-center text-sm mt-1">
              <div>
                <p className="font-medium text-green-500">{batchData.approved}</p>
                <p className="text-xs text-muted-foreground">Goedgekeurd</p>
              </div>
              <div>
                <p className="font-medium text-red-500">{batchData.rejected}</p>
                <p className="text-xs text-muted-foreground">Afgekeurd</p>
              </div>
              <div>
                <p className="font-medium text-blue-500">{batchData.pending}</p>
                <p className="text-xs text-muted-foreground">Wachtend</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card className="md:col-span-2">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Samenvatting</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-1">
            <p className="text-sm">
              Deze reeks bevat <span className="font-medium">{batchData.count}</span> herverdelingsvoorstellen voor
              artikelen uit de collectie <span className="font-medium">{batchData.collection}</span>.
            </p>
            <p className="text-sm">
              Tot nu toe is <span className="font-medium">{progressPercentage}%</span> van de voorstellen verwerkt, met{" "}
              <span className="font-medium text-green-500">{batchData.approved}</span> goedgekeurde en{" "}
              <span className="font-medium text-red-500">{batchData.rejected}</span> afgekeurde voorstellen.
            </p>
            <p className="text-sm">
              Er zijn nog <span className="font-medium text-blue-500">{batchData.pending}</span> voorstellen die op
              beoordeling wachten.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
