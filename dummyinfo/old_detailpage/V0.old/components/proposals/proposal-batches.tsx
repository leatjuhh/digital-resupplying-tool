"use client"

import { useState } from "react"
import Link from "next/link"
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
  const { toast } = useToast()

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

  // Sample data for batches of proposals
  const batches = [
    {
      id: "2025032301",
      date: "23 maart 2025",
      description: "Herverdeling voor week 12 2025",
      count: 42,
      approved: 12,
      rejected: 3,
      pending: 27,
      type: "auto",
    },
    {
      id: "2025031501",
      date: "15 maart 2025",
      description: "Herverdeling voor week 11 2025",
      count: 36,
      approved: 36,
      rejected: 0,
      pending: 0,
      type: "auto",
    },
    {
      id: "2025030201",
      date: "2 maart 2025",
      description: "Restpartijen week 9 2025",
      count: 15,
      approved: 10,
      rejected: 5,
      pending: 0,
      type: "manual",
    },
    {
      id: "2025021501",
      date: "15 februari 2025",
      description: "Herverdeling voor week 7 2025",
      count: 53,
      approved: 48,
      rejected: 5,
      pending: 0,
      type: "auto",
    },
    {
      id: "2025020101",
      date: "1 februari 2025",
      description: "Herverdeling voor week 5 2025",
      count: 28,
      approved: 21,
      rejected: 7,
      pending: 0,
      type: "auto",
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reeksen Herverdelingsvoorstellen</CardTitle>
        <CardDescription>Overzicht van alle gegenereerde reeksen met herverdelingsvoorstellen</CardDescription>
      </CardHeader>
      <CardContent>
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
              {batches.map((batch) => {
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
      </CardContent>
    </Card>
  )
}
