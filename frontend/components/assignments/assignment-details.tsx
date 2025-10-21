"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Check, ChevronDown, ChevronUp, X } from "lucide-react"
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import Link from "next/link"

interface AssignmentDetailsProps {
  id: string
}

export function AssignmentDetails({ id }: AssignmentDetailsProps) {
  const [sortField, setSortField] = useState<string | null>("article")
  const [sortDirection, setSortDirection] = useState<"asc" | "desc" | null>("asc")
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false)
  const [failDialogOpen, setFailDialogOpen] = useState(false)
  const [selectedAssignment, setSelectedAssignment] = useState<any | null>(null)
  const [failReason, setFailReason] = useState("")
  const [failSize, setFailSize] = useState("")
  const { toast } = useToast()

  const handleSort = (field: string) => {
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

  const getSortIcon = (field: string) => {
    if (sortField !== field) return null
    return sortDirection === "asc" ? <ChevronUp className="ml-1 h-4 w-4" /> : <ChevronDown className="ml-1 h-4 w-4" />
  }

  const handleComplete = () => {
    toast({
      title: "Opdracht voltooid",
      description: `Opdracht voor artikel ${selectedAssignment.article} is gemarkeerd als voltooid.`,
    })
    setCompleteDialogOpen(false)
    setSelectedAssignment(null)
  }

  const handleFail = () => {
    if (!failReason || !failSize) {
      toast({
        title: "Informatie ontbreekt",
        description: "Selecteer een maat en geef een reden op waarom de opdracht niet kon worden uitgevoerd.",
        variant: "destructive",
      })
      return
    }

    toast({
      title: "Opdracht niet uitgevoerd",
      description: `Opdracht voor artikel ${selectedAssignment.article} (maat ${failSize}) is gemarkeerd als niet uitgevoerd.`,
    })
    setFailDialogOpen(false)
    setSelectedAssignment(null)
    setFailReason("")
    setFailSize("")
  }

  // Sample data for assignments
  const assignments = [
    {
      id: "1",
      article: "TC039-04",
      description: "Brisia Peacock Top",
      fromStore: "Etten-Leur",
      toStore: "Panningen",
      sizes: ["M"],
      status: "Open",
    },
    {
      id: "2",
      article: "LR552-12",
      description: "Pipa T-Shirt",
      fromStore: "Etten-Leur",
      toStore: "Tilburg",
      sizes: ["S", "M"],
      status: "Voltooid",
    },
    {
      id: "3",
      article: "BT778-05",
      description: "Liza Blouse",
      fromStore: "Etten-Leur",
      toStore: "Brunssum",
      sizes: ["L", "XL"],
      status: "Open",
    },
    {
      id: "4",
      article: "DR221-08",
      description: "Flower Summer Dress",
      fromStore: "Etten-Leur",
      toStore: "Kerkrade",
      sizes: ["S"],
      status: "Niet uitgevoerd",
      reason: "Artikel niet vindbaar",
      failedSize: "S",
    },
    {
      id: "5",
      article: "JK102-01",
      description: "Denim Jacket",
      fromStore: "Etten-Leur",
      toStore: "Weert",
      sizes: ["M", "L"],
      status: "Open",
    },
  ]

  // Sample data for the series
  const seriesData = {
    id,
    description: "Herverdeling voor week 11 2025",
    date: "15 maart 2025",
    count: 12,
    completed: 5,
    pending: 7,
    status: "In behandeling",
    store: "Etten-Leur",
  }

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
              <p className="text-sm">Datum: {seriesData.date}</p>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Voortgang</h3>
              <p className="font-medium">
                {seriesData.completed} van {seriesData.count} opdrachten verwerkt (
                {Math.round((seriesData.completed / seriesData.count) * 100)}%)
              </p>
              <div className="h-2 w-full rounded-full bg-secondary mt-2">
                <div
                  className="h-full rounded-full bg-blue-500"
                  style={{ width: `${Math.round((seriesData.completed / seriesData.count) * 100)}%` }}
                />
              </div>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Status</h3>
              <div className="flex items-center gap-2">
                <Badge variant="outline">{seriesData.status}</Badge>
              </div>
              <p className="text-sm">Uw winkel: {seriesData.store}</p>
              <p className="text-sm">Nog te verwerken: {seriesData.pending} opdrachten</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Te verwerken artikelen</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="cursor-pointer" onClick={() => handleSort("article")}>
                    <div className="flex items-center">Artikelcode {getSortIcon("article")}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer" onClick={() => handleSort("description")}>
                    <div className="flex items-center">Omschrijving {getSortIcon("description")}</div>
                  </TableHead>
                  <TableHead>Van</TableHead>
                  <TableHead>Naar</TableHead>
                  <TableHead>Maten</TableHead>
                  <TableHead className="cursor-pointer" onClick={() => handleSort("status")}>
                    <div className="flex items-center">Status {getSortIcon("status")}</div>
                  </TableHead>
                  <TableHead className="text-right">Acties</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assignments.map((assignment) => (
                  <TableRow key={assignment.id}>
                    <TableCell className="font-medium">{assignment.article}</TableCell>
                    <TableCell>
                      <Link href={`/assignments/${id}/${assignment.id}`} className="hover:underline">
                        {assignment.description}
                      </Link>
                    </TableCell>
                    <TableCell>{assignment.fromStore}</TableCell>
                    <TableCell>{assignment.toStore}</TableCell>
                    <TableCell>{assignment.sizes.join(", ")}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          assignment.status === "Voltooid"
                            ? "default"
                            : assignment.status === "Niet uitgevoerd"
                              ? "destructive"
                              : "outline"
                        }
                      >
                        {assignment.status}
                      </Badge>
                      {assignment.reason && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {assignment.failedSize}: {assignment.reason}
                        </p>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex justify-end gap-1">
                        {assignment.status === "Open" && (
                          <>
                            <Dialog
                              open={completeDialogOpen && selectedAssignment?.id === assignment.id}
                              onOpenChange={(open) => {
                                setCompleteDialogOpen(open)
                                if (!open) setSelectedAssignment(null)
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
                                    Bevestig dat u de herverdeling van artikel {selectedAssignment?.article} (
                                    {selectedAssignment?.description}) heeft uitgevoerd.
                                  </DialogDescription>
                                </DialogHeader>
                                <div className="py-4">
                                  <p>
                                    U bevestigt dat u de volgende maten heeft overgebracht van{" "}
                                    {selectedAssignment?.fromStore} naar {selectedAssignment?.toStore}:
                                  </p>
                                  <p className="font-medium mt-2">{selectedAssignment?.sizes.join(", ")}</p>
                                </div>
                                <DialogFooter>
                                  <Button variant="outline" onClick={() => setCompleteDialogOpen(false)}>
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
                                  setSelectedAssignment(null)
                                  setFailReason("")
                                  setFailSize("")
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
                                    Geef aan waarom de herverdeling van artikel {selectedAssignment?.article} (
                                    {selectedAssignment?.description}) niet kon worden uitgevoerd.
                                  </DialogDescription>
                                </DialogHeader>
                                <div className="py-4 space-y-4">
                                  <div className="space-y-2">
                                    <Label htmlFor="size-select">Voor welke maat?</Label>
                                    <Select value={failSize} onValueChange={setFailSize}>
                                      <SelectTrigger id="size-select">
                                        <SelectValue placeholder="Selecteer een maat" />
                                      </SelectTrigger>
                                      <SelectContent>
                                        {selectedAssignment?.sizes.map((size: string) => (
                                          <SelectItem key={size} value={size}>
                                            {size}
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
                                    <Textarea id="fail-notes" placeholder="Voeg eventueel extra toelichting toe..." />
                                  </div>
                                </div>
                                <DialogFooter>
                                  <Button variant="outline" onClick={() => setFailDialogOpen(false)}>
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
        </CardContent>
      </Card>
    </div>
  )
}
