"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { api, type Batch } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { BarChart, Box, Calendar, ChevronDown, ChevronUp, ClipboardList, Eye } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

type SortDirection = "asc" | "desc" | null
type SortField = "id" | "date" | "count" | "progress" | null

export function ProposalBatches() {
  const [sortField, setSortField] = useState<SortField>("date")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")
  const [convertDialogOpen, setConvertDialogOpen] = useState(false)
  const [selectedBatchId, setSelectedBatchId] = useState<string | null>(null)
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  // Fetch batches from API
  useEffect(() => {
    async function fetchBatches() {
      try {
        setLoading(true)
        const data = await api.batches.getAll()
        setBatches(data)
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

  const handleConvertToAssignments = () => {
    toast({
      title: "Reeks geconverteerd naar opdrachten",
      description: `Reeks #${selectedBatchId} is succesvol geconverteerd naar opdrachten voor de winkels.`,
    })
    setConvertDialogOpen(false)
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
  const transformedBatches = batches.map(batch => ({
    id: batch.id.toString(),
    date: formatDate(batch.created_at),
    description: batch.name,
    count: batch.pdf_count,
    // TODO: Deze data komt later uit de proposals
    approved: 0,
    rejected: 0,
    pending: batch.pdf_count,
    type: "auto" as const,
  }))

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

        {!loading && !error && transformedBatches.length === 0 && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Nog geen batches aangemaakt</p>
          </div>
        )}

        {!loading && !error && transformedBatches.length > 0 && (
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
              {transformedBatches.map((batch) => {
                const progressPercentage = Math.round(((batch.approved + batch.rejected) / batch.count) * 100)
                const isComplete = progressPercentage === 100

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
                              progressPercentage === 100 ? "bg-green-500" : "bg-blue-500"
                            }`}
                            style={{ width: `${progressPercentage}%` }}
                          />
                        </div>
                      </div>
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
                          <Dialog
                            open={convertDialogOpen && selectedBatchId === batch.id}
                            onOpenChange={(open) => {
                              setConvertDialogOpen(open)
                              if (!open) setSelectedBatchId(null)
                            }}
                          >
                            <DialogTrigger asChild>
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-green-600"
                                onClick={() => setSelectedBatchId(batch.id)}
                              >
                                <ClipboardList className="mr-2 h-4 w-4" />
                                Naar Opdrachten
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>Converteer naar Opdrachten</DialogTitle>
                                <DialogDescription>
                                  Weet u zeker dat u deze reeks wilt converteren naar opdrachten voor de winkels? Dit
                                  zal de goedgekeurde voorstellen omzetten in concrete opdrachten die de winkels kunnen
                                  uitvoeren.
                                </DialogDescription>
                              </DialogHeader>
                              <DialogFooter className="mt-4">
                                <Button variant="outline" onClick={() => setConvertDialogOpen(false)}>
                                  Annuleren
                                </Button>
                                <Button
                                  onClick={handleConvertToAssignments}
                                  className="bg-green-600 hover:bg-green-700"
                                >
                                  Converteer naar Opdrachten
                                </Button>
                              </DialogFooter>
                            </DialogContent>
                          </Dialog>
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
