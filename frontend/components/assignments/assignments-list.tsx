"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Calendar, ClipboardCheck, Eye } from "lucide-react"

import { api, type AssignmentSeriesSummary } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

function formatDate(dateValue: string | null) {
  if (!dateValue) return "Onbekend"

  return new Intl.DateTimeFormat("nl-NL", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(dateValue))
}

function statusLabel(status: AssignmentSeriesSummary["status"]) {
  switch (status) {
    case "completed":
      return "Voltooid"
    case "in_progress":
      return "In behandeling"
    case "attention":
      return "Actie nodig"
    default:
      return "Open"
  }
}

function statusVariant(status: AssignmentSeriesSummary["status"]): "default" | "outline" | "destructive" | "secondary" {
  switch (status) {
    case "completed":
      return "default"
    case "attention":
      return "destructive"
    case "in_progress":
      return "outline"
    default:
      return "secondary"
  }
}

export function AssignmentsList() {
  const [series, setSeries] = useState<AssignmentSeriesSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadAssignments() {
      try {
        setLoading(true)
        const response = await api.assignments.list()

        if (!cancelled) {
          setSeries(response.series)
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Failed to load assignments:", err)
          setError(err instanceof Error ? err.message : "Kon opdrachten niet laden")
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadAssignments()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Herverdelingsopdrachten</CardTitle>
        <CardDescription>Echte store-opdrachten op basis van goedgekeurde proposals</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-muted-foreground">Opdrachten laden...</p>
        ) : error ? (
          <p className="text-sm text-destructive">{error}</p>
        ) : series.length === 0 ? (
          <div className="rounded-md border border-dashed p-6 text-sm text-muted-foreground">
            Er zijn momenteel geen opdrachten voor uw winkel.
          </div>
        ) : (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[110px]">Reeks ID</TableHead>
                  <TableHead>Beschrijving</TableHead>
                  <TableHead>Datum</TableHead>
                  <TableHead className="text-center">Aantal</TableHead>
                  <TableHead>Voortgang</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Acties</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {series.map((assignmentSeries) => {
                  const progressPercentage =
                    assignmentSeries.count > 0
                      ? Math.round((assignmentSeries.completed / assignmentSeries.count) * 100)
                      : 0

                  return (
                    <TableRow key={assignmentSeries.id}>
                      <TableCell className="font-medium">#{assignmentSeries.id}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <ClipboardCheck className="h-4 w-4 text-blue-500" />
                          <div>
                            <p>{assignmentSeries.description}</p>
                            <p className="text-xs text-muted-foreground">
                              Batch: {assignmentSeries.batch_name} • Winkel: {assignmentSeries.store_name}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          {formatDate(assignmentSeries.created_at)}
                        </div>
                      </TableCell>
                      <TableCell className="text-center">{assignmentSeries.count}</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span>
                              {assignmentSeries.completed} voltooid, {assignmentSeries.pending} open
                              {assignmentSeries.failed > 0 ? `, ${assignmentSeries.failed} geblokkeerd` : ""}
                            </span>
                            <span className="font-medium">{progressPercentage}%</span>
                          </div>
                          <div className="h-2 w-full rounded-full bg-secondary">
                            <div
                              className={`h-full rounded-full ${
                                assignmentSeries.status === "completed"
                                  ? "bg-green-500"
                                  : assignmentSeries.status === "attention"
                                    ? "bg-red-500"
                                    : "bg-blue-500"
                              }`}
                              style={{ width: `${progressPercentage}%` }}
                            />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusVariant(assignmentSeries.status)}>{statusLabel(assignmentSeries.status)}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button asChild variant="ghost" size="sm">
                          <Link href={`/assignments/${assignmentSeries.id}`}>
                            <Eye className="mr-2 h-4 w-4" />
                            Bekijken
                          </Link>
                        </Button>
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
