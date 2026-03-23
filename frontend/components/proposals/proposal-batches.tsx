"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { api } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { BarChart, Box, Calendar, ChevronDown, ChevronUp, ClipboardList, Eye } from "lucide-react"

type SortDirection = "asc" | "desc" | null
type SortField = "id" | "date" | "count" | "progress" | null

export function ProposalBatches() {
  const [sortField, setSortField] = useState<SortField>("date")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")
  const [batches, setBatches] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch PDF batches with proposals from API
  useEffect(() => {
    async function fetchBatches() {
      try {
        setLoading(true)
        const data = await api.pdf.getBatches()
        
        // Fetch proposals for each batch
        const batchesWithProposals = await Promise.all(
          data.map(async (batch) => {
            try {
              const proposalsData = await api.pdf.getBatchProposals(batch.id)
              return {
                ...batch,
                proposals: proposalsData.proposals || [],
                status_counts: proposalsData.status_counts || {
                  pending: 0,
                  approved: 0,
                  rejected: 0,
                  edited: 0
                }
              }
            } catch (err) {
              console.error(`Failed to fetch proposals for batch ${batch.id}:`, err)
              return {
                ...batch,
                proposals: [],
                status_counts: { pending: 0, approved: 0, rejected: 0, edited: 0 }
              }
            }
          })
        )
        
        setBatches(batchesWithProposals)
        setError(null)
      } catch (err) {
        console.error('Failed to fetch batches:', err)
        setError('Kon batches niet ophalen. Is de backend server actief?')
      } finally {
        setLoading(false)
      }
    }

    fetchBatches()
  }, [])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      if (sortDirection === "asc") {
        setSortDirection("desc")
      } else if (sortDirection === "desc") {
        setSortField(null)
        setSortDirection(null)
      }
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return null
    return sortDirection === "asc" ? <ChevronUp className="ml-1 h-4 w-4" /> : <ChevronDown className="ml-1 h-4 w-4" />
  }

  // Format date from ISO string to readable format
  const formatDate = (isoDate: string) => {
    const date = new Date(isoDate)
    return date.toLocaleDateString('nl-NL', { 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric' 
    })
  }

  // Transform API data to component format
  const transformedBatches = batches.map(batch => {
    const totalProposals = batch.proposals?.length || 0
    const statusCounts = batch.status_counts || {
      pending: 0,
      approved: 0,
      rejected: 0,
      edited: 0
    }
    
    // Calculate actual totals from status counts (more reliable than proposals.length)
    const actualTotal = statusCounts.approved + statusCounts.rejected + statusCounts.pending + statusCounts.edited
    const count = actualTotal > 0 ? actualTotal : totalProposals
    
    return {
      id: batch.id.toString(),
      createdAt: batch.created_at,
      date: formatDate(batch.created_at),
      description: batch.naam || batch.name,
      count: count,
      approved: statusCounts.approved,
      rejected: statusCounts.rejected,
      pending: statusCounts.pending,
      edited: statusCounts.edited,
      type: "auto" as const,
    }
  })

  const sortedBatches = [...transformedBatches].sort((left, right) => {
    if (!sortField || !sortDirection) {
      return 0
    }

    const direction = sortDirection === "asc" ? 1 : -1

    switch (sortField) {
      case "id":
        return (Number(left.id) - Number(right.id)) * direction
      case "date":
        return (new Date(left.createdAt).getTime() - new Date(right.createdAt).getTime()) * direction
      case "count":
        return (left.count - right.count) * direction
      case "progress": {
        const leftProgress = Math.round(((left.approved + left.rejected) / Math.max(left.count, 1)) * 100)
        const rightProgress = Math.round(((right.approved + right.rejected) / Math.max(right.count, 1)) * 100)
        return (leftProgress - rightProgress) * direction
      }
      default:
        return 0
    }
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reeksen Herverdelingsvoorstellen</CardTitle>
        <CardDescription>Overzicht van alle gegenereerde reeksen met herverdelingsvoorstellen</CardDescription>
      </CardHeader>
      <CardContent>
        {loading && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Batches laden...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <p className="text-destructive">{error}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Zorg dat de backend draait op http://localhost:8000
            </p>
          </div>
        )}

        {!loading && !error && sortedBatches.length === 0 && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Nog geen batches aangemaakt</p>
          </div>
        )}

        {!loading && !error && sortedBatches.length > 0 && (
          <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px] cursor-pointer" onClick={() => handleSort("id")}>
                  <div className="flex items-center">Reeks ID {getSortIcon("id")}</div>
                </TableHead>
                <TableHead className="min-w-[180px]">Beschrijving</TableHead>
                <TableHead className="cursor-pointer" onClick={() => handleSort("date")}>
                  <div className="flex items-center">Datum {getSortIcon("date")}</div>
                </TableHead>
                <TableHead className="cursor-pointer text-center" onClick={() => handleSort("count")}>
                  <div className="flex items-center justify-center">Aantal {getSortIcon("count")}</div>
                </TableHead>
                <TableHead className="cursor-pointer" onClick={() => handleSort("progress")}>
                  <div className="flex items-center">Voortgang {getSortIcon("progress")}</div>
                </TableHead>
                <TableHead className="text-right">Acties</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedBatches.map((batch) => {
                // Calculate progress percentage safely (avoid NaN)
                const reviewed = batch.approved + batch.rejected
                const progressPercentage = batch.count > 0 
                  ? Math.round((reviewed / batch.count) * 100)
                  : 0
                const isComplete = progressPercentage === 100 && batch.count > 0

                return (
                  <TableRow key={batch.id}>
                    <TableCell className="font-medium">#{batch.id}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {batch.type === "auto" ? (
                          <BarChart className="h-4 w-4 text-blue-500" />
                        ) : (
                          <Box className="h-4 w-4 text-orange-500" />
                        )}
                        <span>{batch.description}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        {batch.date}
                      </div>
                    </TableCell>
                    <TableCell className="text-center">{batch.count}</TableCell>
                    <TableCell>
                      {batch.count === 0 ? (
                        <div className="text-xs text-muted-foreground">
                          Nog geen voorstellen gegenereerd
                        </div>
                      ) : (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span>
                              {batch.approved} goedgekeurd, {batch.rejected} afgekeurd
                              {batch.pending > 0 && `, ${batch.pending} wachtend`}
                            </span>
                            <span className="font-medium">{progressPercentage}%</span>
                          </div>
                          <div className="h-2 w-full rounded-full bg-secondary">
                            <div
                              className={`h-full rounded-full ${
                                isComplete ? "bg-green-500" : "bg-blue-500"
                              }`}
                              style={{ width: `${progressPercentage}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button asChild variant="ghost" size="sm">
                          <Link href={`/proposals/batch/${batch.id}`}>
                            <Eye className="mr-2 h-4 w-4" />
                            Bekijken
                          </Link>
                        </Button>

                        {isComplete && (
                          <Button asChild variant="outline" size="sm" className="text-green-600">
                            <Link href="/assignments">
                              <ClipboardList className="mr-2 h-4 w-4" />
                              Opdrachten
                            </Link>
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
