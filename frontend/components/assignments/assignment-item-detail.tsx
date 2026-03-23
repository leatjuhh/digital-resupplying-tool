"use client"

import { useEffect, useState } from "react"
import { Check, X } from "lucide-react"

import { api, type AssignmentItemDetail as AssignmentItemDetailData, type AssignmentSeriesSummary } from "@/lib/api"
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

interface AssignmentItemDetailProps {
  id: string
  assignmentId: string
}

function statusVariant(status: AssignmentItemDetailData["status"]): "default" | "outline" | "destructive" {
  switch (status) {
    case "completed":
      return "default"
    case "failed":
      return "destructive"
    default:
      return "outline"
  }
}

function statusLabel(status: AssignmentItemDetailData["status"]) {
  switch (status) {
    case "completed":
      return "Voltooid"
    case "failed":
      return "Niet uitgevoerd"
    default:
      return "Open"
  }
}

export function AssignmentItemDetail({ id, assignmentId }: AssignmentItemDetailProps) {
  const [series, setSeries] = useState<AssignmentSeriesSummary | null>(null)
  const [assignment, setAssignment] = useState<AssignmentItemDetailData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false)
  const [failDialogOpen, setFailDialogOpen] = useState(false)
  const [completeNotes, setCompleteNotes] = useState("")
  const [failReason, setFailReason] = useState("")
  const [failSize, setFailSize] = useState("")
  const [failNotes, setFailNotes] = useState("")
  const { toast } = useToast()

  async function loadAssignment() {
    try {
      setLoading(true)
      const data = await api.assignments.getItem(Number.parseInt(id, 10), Number.parseInt(assignmentId, 10))
      setSeries(data.series)
      setAssignment(data.item)
      setError(null)
    } catch (err) {
      console.error("Failed to fetch assignment item:", err)
      setError(err instanceof Error ? err.message : "Kon opdrachtitem niet laden")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAssignment()
  }, [assignmentId, id])

  const resetDialogs = () => {
    setCompleteDialogOpen(false)
    setFailDialogOpen(false)
    setCompleteNotes("")
    setFailReason("")
    setFailSize("")
    setFailNotes("")
  }

  const handleComplete = async () => {
    if (!assignment) return

    try {
      await api.assignments.complete(assignment.assignment_id, completeNotes || undefined)
      toast({
        title: "Opdracht voltooid",
        description: `Artikel ${assignment.artikelnummer} is bijgewerkt.`,
      })
      resetDialogs()
      await loadAssignment()
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
    if (!assignment || !failReason || !failSize) {
      toast({
        title: "Informatie ontbreekt",
        description: "Selecteer een maat en geef een reden op.",
        variant: "destructive",
      })
      return
    }

    try {
      await api.assignments.fail(assignment.assignment_id, failReason, failSize, failNotes || undefined)
      toast({
        title: "Opdracht bijgewerkt",
        description: `Artikel ${assignment.artikelnummer} is als niet uitvoerbaar gemarkeerd.`,
      })
      resetDialogs()
      await loadAssignment()
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
    return <p className="text-sm text-muted-foreground">Opdrachtitem laden...</p>
  }

  if (error || !assignment || !series) {
    return <p className="text-sm text-destructive">{error || "Geen data beschikbaar"}</p>
  }

  const totalSold = assignment.stores.reduce((sum, store) => sum + store.sold, 0)
  const movedSummary = assignment.size_quantities.map((entry) => `${entry.size}: ${entry.qty}`).join(", ")

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-xl">Artikel Informatie</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Artikel</h3>
              <p className="font-medium">{assignment.article_name}</p>
              <p className="text-sm">Code: {assignment.artikelnummer}</p>
              <p className="text-sm">Batch: {series.batch_name}</p>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Route</h3>
              <p className="font-medium">
                {assignment.from_store_name} → {assignment.to_store_name}
              </p>
              <p className="text-sm">Maten: {movedSummary}</p>
              <p className="text-sm">Totaal: {assignment.total_quantity} stuks</p>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Details</h3>
              <p className="text-sm">Leverancier: {assignment.metadata?.Leverancier || "Onbekend"}</p>
              <p className="text-sm">Kleur: {assignment.metadata?.Kleur || "Onbekend"}</p>
              <p className="text-sm">Collectie: {assignment.metadata?.Collectie || "Onbekend"}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Herverdelingsopdracht</CardTitle>
            <Badge variant={statusVariant(assignment.status)}>{statusLabel(assignment.status)}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {assignment.failure_reason && (
            <div className="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              Niet uitgevoerd voor maat {assignment.failure_size}: {assignment.failure_reason}
              {assignment.failure_notes ? ` • ${assignment.failure_notes}` : ""}
            </div>
          )}

          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[120px] font-bold">Filiaal</TableHead>
                  {assignment.sizes.map((size) => (
                    <TableHead key={size} className="text-center min-w-[50px]">
                      {size}
                    </TableHead>
                  ))}
                  <TableHead className="text-center font-bold">Verkocht</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assignment.stores.map((store) => (
                  <TableRow key={store.id}>
                    <TableCell>
                      {store.id} {store.name}
                      {store.id === assignment.from_store_code && (
                        <Badge variant="outline" className="ml-2">
                          Van
                        </Badge>
                      )}
                      {store.id === assignment.to_store_code && (
                        <Badge variant="outline" className="ml-2">
                          Naar
                        </Badge>
                      )}
                    </TableCell>
                    {store.inventory_current.map((qty, index) => {
                      const proposed = store.inventory_proposed[index]
                      const hasDiff = qty !== proposed

                      return (
                        <TableCell key={`${store.id}-${assignment.sizes[index]}`} className="text-center p-0">
                          <div className="grid grid-cols-1">
                            <div className={`py-2 ${hasDiff ? "bg-green-100" : ""}`}>{qty > 0 ? qty : "."}</div>
                            {hasDiff && <div className="border-t bg-blue-100 py-2">{proposed > 0 ? proposed : "."}</div>}
                          </div>
                        </TableCell>
                      )
                    })}
                    <TableCell className="text-center">{store.sold > 0 ? store.sold : "."}</TableCell>
                  </TableRow>
                ))}
                <TableRow className="bg-muted/50 font-medium">
                  <TableCell>Totaal verkocht</TableCell>
                  {assignment.sizes.map((size) => (
                    <TableCell key={`total-${size}`} className="text-center">
                      .
                    </TableCell>
                  ))}
                  <TableCell className="text-center">{totalSold}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>

          <div className="mt-3 text-sm text-muted-foreground">
            <p>Legenda:</p>
            <div className="mt-1 flex items-center gap-4">
              <div className="flex items-center">
                <div className="mr-2 h-4 w-4 bg-green-100" />
                <span>Huidige voorraad</span>
              </div>
              <div className="flex items-center">
                <div className="mr-2 h-4 w-4 bg-blue-100" />
                <span>Voorraad na deze opdracht</span>
              </div>
            </div>
          </div>

          {assignment.status === "open" && (
            <div className="mt-6 flex justify-end gap-2">
              <Dialog open={completeDialogOpen} onOpenChange={setCompleteDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-green-600 hover:bg-green-700">
                    <Check className="mr-2 h-4 w-4" />
                    Markeer als voltooid
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Opdracht voltooien</DialogTitle>
                    <DialogDescription>
                      Bevestig dat u {assignment.artikelnummer} heeft verplaatst van {assignment.from_store_name} naar{" "}
                      {assignment.to_store_name}.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-3 py-4">
                    <p className="text-sm">Maten: {movedSummary}</p>
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

              <Dialog open={failDialogOpen} onOpenChange={setFailDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="text-red-500">
                    <X className="mr-2 h-4 w-4" />
                    Kan niet uitvoeren
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Opdracht niet uitgevoerd</DialogTitle>
                    <DialogDescription>
                      Geef aan waarom de herverdeling van artikel {assignment.artikelnummer} niet kon worden uitgevoerd.
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
                          {assignment.size_quantities.map((entry) => (
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
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
