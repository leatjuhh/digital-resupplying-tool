"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

interface BatchWithStats {
  id: number
  title: string
  date: string
  totalProposals: number
  assessedProposals: number
  nextProposalId: string | null
}

export function PendingProposals() {
  const [batches, setBatches] = useState<BatchWithStats[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadBatches = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const { api } = await import('@/lib/api')
        
        // Get all batches
        const allBatches = await api.pdf.getBatches()
        
        // Process batches with proposals
        const batchesWithStats: BatchWithStats[] = []
        
        for (const batch of allBatches.slice(0, 4)) { // Limit to 4 most recent
          try {
            const batchDetails = await api.pdf.getBatchProposals(batch.id)
            
            // Calculate assessed proposals (approved + rejected + edited)
            const assessedCount = 
              batchDetails.status_counts.approved +
              batchDetails.status_counts.rejected +
              batchDetails.status_counts.edited
            
            // Find first pending proposal
            const pendingProposal = batchDetails.proposals.find(p => p.status === 'pending')
            
            batchesWithStats.push({
              id: batch.id,
              title: batch.naam,
              date: new Date(batch.created_at).toLocaleDateString('nl-NL', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              }),
              totalProposals: batchDetails.total_proposals,
              assessedProposals: assessedCount,
              nextProposalId: pendingProposal ? pendingProposal.id.toString() : null
            })
          } catch (err) {
            console.error(`Failed to load proposals for batch ${batch.id}:`, err)
            // Skip this batch if proposals can't be loaded
          }
        }
        
        // Filter only batches with pending proposals
        const pendingBatches = batchesWithStats.filter(b => 
          b.assessedProposals < b.totalProposals
        )
        
        setBatches(pendingBatches)
      } catch (err) {
        console.error('Failed to load batches:', err)
        setError('Kon reeksen niet laden')
      } finally {
        setLoading(false)
      }
    }
    
    loadBatches()
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center">
          <div className="grid gap-1">
            <CardTitle>Wachtende Reeksen</CardTitle>
            <p className="text-sm text-muted-foreground">Reeksen met voorstellen die op beoordeling wachten</p>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
                <Skeleton className="h-2 w-full" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Wachtende Reeksen</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (batches.length === 0) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center">
          <div className="grid gap-1">
            <CardTitle>Wachtende Reeksen</CardTitle>
            <p className="text-sm text-muted-foreground">Reeksen met voorstellen die op beoordeling wachten</p>
          </div>
          <Button asChild variant="ghost" size="sm" className="ml-auto">
            <Link href="/proposals">Alle bekijken</Link>
          </Button>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Geen wachtende voorstellen. Alle reeksen zijn volledig beoordeeld! 🎉
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center">
        <div className="grid gap-1">
          <CardTitle>Wachtende Reeksen</CardTitle>
          <p className="text-sm text-muted-foreground">Reeksen met voorstellen die op beoordeling wachten</p>
        </div>
        <Button asChild variant="ghost" size="sm" className="ml-auto">
          <Link href="/proposals">Alle bekijken</Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {batches.map((batch) => {
            const progressPercentage = Math.round((batch.assessedProposals / batch.totalProposals) * 100)

            return (
              <div key={batch.id} className="flex flex-col space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium leading-none">
                      <Link href={`/proposals/batch/${batch.id}`} className="hover:underline">
                        {batch.title}
                      </Link>
                    </p>
                    <div className="flex items-center pt-1">
                      <p className="text-sm text-muted-foreground">{batch.date}</p>
                      <span className="px-1 text-muted-foreground">·</span>
                      <p className="text-sm text-muted-foreground">{batch.totalProposals} voorstellen</p>
                    </div>
                  </div>
                  {batch.nextProposalId && (
                    <Button asChild size="sm" variant="outline" className="h-8">
                      <Link href={`/proposals/${batch.nextProposalId}`}>
                        <span className="mr-1">Beoordelen</span>
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  )}
                </div>

                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span>
                      {batch.assessedProposals} van {batch.totalProposals} beoordeeld
                    </span>
                    <span className="font-medium">{progressPercentage}%</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-secondary">
                    <div className="h-full rounded-full bg-blue-500" style={{ width: `${progressPercentage}%` }} />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
