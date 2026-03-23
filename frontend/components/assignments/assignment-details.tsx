"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Check, X } from "lucide-react"

import { api, type AssignmentItemSummary, type AssignmentSeriesDetail } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"

interface AssignmentDetailsProps {
  id: string
}

function statusLabel(status: AssignmentItemSummary["status"]) {
  switch (status) {
    case "completed":
      return "Voltooid"
    case "failed":
      return "Niet uitgevoerd"
    default:
      return "Open"
  }
}

function statusVariant(status: AssignmentItemSummary["status"]): "default" | "outline" | "destructive" {
  switch (status) {
    case "completed":
      return "default"
    case "failed":
      return "destructive"
    default:
      return "outline"
  }
}

export function AssignmentDetails({ id }: AssignmentDetailsProps) {
  const [seriesData, setSeriesData] = useState<AssignmentSeriesDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false)
  const [failDialogOpen, setFailDialogOpen] = useState(false)
  const [selectedAssignment, setSelectedAssignment] = useState<AssignmentItemSummary | null>(null)
  const [completeNotes, setCompleteNotes] = useState("")
  const [failReason, setFailReason] = useState("")
  const [failSize, setFailSize] = useState("")
  const [failNotes, setFailNotes] = useState("")
  const { toast } = useToast()

  async function loadSeries() {
    try {
      setLoading(true)
      const data = await api.assignments.getSeries(Number.parseInt(id, 10))
      setSeriesData(data)
      setError(null)
    } catch (err) {
      console.error("Failed to fetch assignment series:", err)
      setError(err instanceof Error ? err.message : "Kon opdrachtreeks niet laden")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSeries()
  }, [id])

  const resetDialogs = () => {
    setCompleteDialogOpen(false)
    setFailDialogOpen(false)
    setSelectedAssignment(null)
    setCompleteNotes("")
    setFailReason("")
    setFailSize("")
    setFailNotes("")
  }

  const handleComplete = async () => {
    if (!selectedAssignment) return

    try {
      await api.assignments.complete(selectedAssignment.id, completeNotes || undefined)
      toast({
        title: "Opdracht voltooid",
        description: `Opdracht voor artikel ${selectedAssignment.artikelnummer} is bijgewerkt.`,
      })
      resetDialogs()
      await loadSeries()
    } catch (err) {
      console.error("Failed to complete assignment:", err)
      toast({
        title: "Fout",
        description: err instanceof Error ? err.message : "Kon opdracht niet voltooien",
        variant: "destructive",
      })
    }
  }

  const handleFail = async () => {
    if (!selectedAssignment || !failReason || !failSize) {
      toast({
        title: "Informatie ontbreekt",
        description: "Selecteer een maat en geef een reden op.",
        variant: "destructive",
      })
      return
    }

    try {
      await api.assignments.fail(selectedAssignment.id, failReason, failSize, failNotes || undefined)
      toast({
        title: "Opdracht bijgewerkt",
        description: `Opdracht voor artikel ${selectedAssignment.artikelnummer} is als niet uitvoerbaar gemarkeerd.`,
      })
      resetDialogs()
      await loadSeries()
    } catch (err) {
      console.error("Failed to fail assignment:", err)
      toast({
        title: "Fout",
        description: err instanceof Error ? err.message : "Kon opdracht niet bijwerken",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return <p className="text-sm text-muted-foreground">Opdrachtreeks laden...</p>
  }

  if (error || !seriesData) {
    return <p className="text-sm text-destructive">{error || "Geen data beschikbaar"}</p>
  }

  const progressPercentage = seriesData.count > 0 ? Math.round((seriesData.completed / seriesData.count) * 100) : 0

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-xl">Opdracht Informatie</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Reeks</h3>
              <p className="font-medium">{seriesData.description}</p>
              <p className="text-sm">ID: #{seriesData.id}</p>
              <p className="text-sm">Batch: {seriesData.batch_name}</p>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Voortgang</h3>
              <p className="font-medium">
                {seriesData.completed} van {seriesData.count} opdrachten voltooid ({progressPercentage}%)
              </p>
              <div className="mt-2 h-2 w-full rounded-full bg-secondary">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${progressPercentage}%` }} />
              </div>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Winkel</h3>
              <p className="font-medium">
                {seriesData.store_code} {seriesData.store_name}
              </p>
              <p className="text-sm">Nog open: {seriesData.pending}</p>
              <p className="text-sm">Geblokkeerd: {seriesData.failed}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Te verwerken artikelen</CardTitle>
        </CardHeader>
        <CardContent>
          {seriesData.items.length === 0 ? (
            <div className="rounded-md border border-dashed p-6 text-sm text-muted-foreground">
              Deze reeks bevat nog geen assignment-items.
            </div>
          ) : (
            <div className="rounded-md border overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Artikelcode</TableHead>
                    <TableHead>Omschrijving</TableHead>
                    <TableHead>Van</TableHead>
                    <TableHead>Naar</TableHead>
                    <TableHead>Maten</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Acties</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {seriesData.items.map((assignment) => (
                    <TableRow key={assignment.id}>
                      <TableCell className="font-medium">{assignment.artikelnummer}</TableCell>
                      <TableCell>
                        <Link href={`/assignments/${id}/${assignment.id}`} className="hover:underline">
                          {assignment.article_name}
                        </Link>
                      </TableCell>
                      <TableCell>{assignment.from_store_name}</TableCell>
                      <TableCell>{assignment.to_store_name}</TableCell>
                      <TableCell>
                        {assignment.size_quantities.map((entry) => `${entry.size} (${entry.qty})`).join(", ")}
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusVariant(assignment.status)}>{statusLabel(assignment.status)}</Badge>
                        {assignment.failure_reason && (
                          <p className="mt-1 text-xs text-muted-foreground">
                            {assignment.failure_size}: {assignment.failure_reason}
                          </p>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex justify-end gap-1">
                          {assignment.status === "open" && (
                            <>
                              <Dialog
                                open={completeDialogOpen && selectedAssignment?.id === assignment.id}
                                onOpenChange={(open) => {
                                  setCompleteDialogOpen(open)
                                  if (!open) {
                                    resetDialogs()
                                  }
                                }}
                              >
                                <DialogTrigger asChild>
                                  <Button
                                    size="icon"
                                    variant="ghost"
                                    className="h-8 w-8 text-green-500"
                                    onClick={() => setSelectedAssignment(assignment)}
                                  >
                                    <Check className="h-4 w-4" />
                                    <span className="sr-only">Voltooid</span>
                                  </Button>
                                </DialogTrigger>
                                <DialogContent>
                                  <DialogHeader>
                                    <DialogTitle>Opdracht voltooien</DialogTitle>
                                    <DialogDescription>
                                      Bevestig dat artikel {selectedAssignment?.artikelnummer} is verplaatst van{" "}
                                      {selectedAssignment?.from_store_name} naar {selectedAssignment?.to_store_name}.
                                    </DialogDescription>
                                  </DialogHeader>
                                  <div className="space-y-3 py-4">
                                    <p className="text-sm">
                                      Maten: {selectedAssignment?.size_quantities.map((entry) => `${entry.size} (${entry.qty})`).join(", ")}
                                    </p>
                                    <div className="space-y-2">
                                      <Label htmlFor="complete-notes">Toelichting (optioneel)</Label>
                                      <Textarea
                                        id="complete-notes"
                                        value={completeNotes}
                                        onChange={(event) => setCompleteNotes(event.target.value)}
                                        placeholder="Optionele notitie voor deze uitvoering..."
                                      />
                                    </div>
                                  </div>
                                  <DialogFooter>
                                    <Button variant="outline" onClick={resetDialogs}>
                                      Annuleren
                                    </Button>
                                    <Button onClick={handleComplete} className="bg-green-600 hover:bg-green-700">
                                      Bevestigen
                                    </Button>
                                  </DialogFooter>
                                </DialogContent>
                              </Dialog>

                              <Dialog
                                open={failDialogOpen && selectedAssignment?.id === assignment.id}
                                onOpenChange={(open) => {
                                  setFailDialogOpen(open)
                                  if (!open) {
                                    resetDialogs()
                                  }
                                }}
                              >
                                <DialogTrigger asChild>
                                  <Button
                                    size="icon"
                                    variant="ghost"
                                    className="h-8 w-8 text-red-500"
                                    onClick={() => setSelectedAssignment(assignment)}
                                  >
                                    <X className="h-4 w-4" />
                                    <span className="sr-only">Niet mogelijk</span>
                                  </Button>
                                </DialogTrigger>
                                <DialogContent>
                                  <DialogHeader>
                                    <DialogTitle>Opdracht niet uitgevoerd</DialogTitle>
                                    <DialogDescription>
                                      Geef aan waarom artikel {selectedAssignment?.artikelnummer} niet kon worden verwerkt.
                                    </DialogDescription>
                                  </DialogHeader>
                                  <div className="space-y-4 py-4">
                                    <div className="space-y-2">
                                      <Label htmlFor="size-select">Voor welke maat?</Label>
                                      <Select value={failSize} onValueChange={setFailSize}>
                                        <SelectTrigger id="size-select">
                                          <SelectValue placeholder="Selecteer een maat" />
                                        </SelectTrigger>
                                        <SelectContent>
                                          {selectedAssignment?.size_quantities.map((entry) => (
                                            <SelectItem key={entry.size} value={entry.size}>
                                              {entry.size}
                                            </SelectItem>
                                          ))}
                                        </SelectContent>
                                      </Select>
                                    </div>

                                    <div className="space-y-2">
                                      <Label htmlFor="fail-reason">Reden</Label>
                                      <Select value={failReason} onValueChange={setFailReason}>
                                        <SelectTrigger id="fail-reason">
                                          <SelectValue placeholder="Selecteer een reden" />
                                        </SelectTrigger>
                                        <SelectContent>
                                          <SelectItem value="Artikel reeds verkocht">Artikel reeds verkocht</SelectItem>
                                          <SelectItem value="Artikel niet vindbaar">Artikel niet vindbaar</SelectItem>
                                          <SelectItem value="Artikel gereserveerd voor klant">
                                            Artikel gereserveerd voor klant
                                          </SelectItem>
                                        </SelectContent>
                                      </Select>
                                    </div>

                                    <div className="space-y-2">
                                      <Label htmlFor="fail-notes">Toelichting (optioneel)</Label>
                                      <Textarea
                                        id="fail-notes"
                                        value={failNotes}
                                        onChange={(event) => setFailNotes(event.target.value)}
                                        placeholder="Voeg eventueel extra toelichting toe..."
                                      />
                                    </div>
                                  </div>
                                  <DialogFooter>
                                    <Button variant="outline" onClick={resetDialogs}>
                                      Annuleren
                                    </Button>
                                    <Button onClick={handleFail} variant="destructive">
                                      Bevestigen
                                    </Button>
                                  </DialogFooter>
                                </DialogContent>
                              </Dialog>
                            </>
                          )}

                          <Button asChild size="sm" variant="ghost">
                            <Link href={`/assignments/${id}/${assignment.id}`}>Details</Link>
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
