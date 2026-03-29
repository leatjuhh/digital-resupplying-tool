"use client"

import { useEffect, useState } from "react"
import { Brain, Database, GitCompareArrows, TrendingUp } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { api, type ExternalAlgorithmDatasetStatus } from "@/lib/api"

function formatPercent(value?: number | null) {
  if (value === null || value === undefined) {
    return "n.v.t."
  }
  return `${Math.round(value * 1000) / 10}%`
}

function modeLabel(mode: string) {
  if (mode === "rank_assist") return "Ranking assist"
  if (mode === "shadow") return "Shadow"
  return "Uit"
}

export function ExternalAlgorithmStatus() {
  const [status, setStatus] = useState<ExternalAlgorithmDatasetStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchStatus() {
      try {
        setLoading(true)
        const payload = await api.externalAlgorithm.getStatus()
        setStatus(payload)
        setError(null)
      } catch (err) {
        console.error("Failed to load external algorithm status:", err)
        setError("Kon externe algoritmestatus niet laden.")
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5" />
          Externe Algoritmestatus
        </CardTitle>
        <CardDescription>
          Read-only leersignalen uit het aparte herverdelingsalgoritmeproject.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading && <p className="text-sm text-muted-foreground">Status laden...</p>}

        {!loading && error && (
          <Alert variant="destructive">
            <AlertTitle>Geen koppeling beschikbaar</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {!loading && !error && status && !status.data_available && (
          <Alert>
            <AlertTitle>Geen artefacten gevonden</AlertTitle>
            <AlertDescription>
              DRT ziet nog geen bruikbare week- of aggregate-artefacten onder de ingestelde dataset root.
            </AlertDescription>
          </Alert>
        )}

        {!loading && !error && status && status.data_available && (
          <>
            <div className="flex flex-wrap gap-3">
              <Badge variant="outline" className="gap-1">
                <Database className="h-3.5 w-3.5" />
                {status.processed_week_count} week(en)
              </Badge>
              <Badge variant="outline" className="gap-1">
                <GitCompareArrows className="h-3.5 w-3.5" />
                Modus: {modeLabel(status.assist_mode)}
              </Badge>
              {status.latest_week && (
                <Badge variant="secondary">
                  Laatste week: {status.latest_year}-W{status.latest_week}
                </Badge>
              )}
            </div>

            <div className="grid gap-4 md:grid-cols-4">
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Trainingsvoorbeelden</p>
                <p className="mt-1 text-2xl font-semibold">
                  {status.aggregate_training_summary?.total_example_count ?? 0}
                </p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Positieve voorbeelden</p>
                <p className="mt-1 text-2xl font-semibold">
                  {status.aggregate_training_summary?.total_positive_count ?? 0}
                </p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Positive rate</p>
                <p className="mt-1 text-2xl font-semibold">
                  {formatPercent(status.aggregate_training_summary?.positive_rate)}
                </p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Model top-k recall</p>
                <p className="mt-1 text-2xl font-semibold">
                  {formatPercent(status.aggregate_model_summary.top_k_recall_test)}
                </p>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Week</TableHead>
                      <TableHead className="text-right">Observed</TableHead>
                      <TableHead className="text-right">Model kansen</TableHead>
                      <TableHead className="text-right">Overlap</TableHead>
                      <TableHead className="text-right">Recall</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {status.weeks_available.map((week) => (
                      <TableRow key={`${week.year}-${week.week}`}>
                        <TableCell className="font-medium">
                          {week.year}-W{week.week}
                        </TableCell>
                        <TableCell className="text-right">{week.observed_move_count}</TableCell>
                        <TableCell className="text-right">{week.model_opportunity_count}</TableCell>
                        <TableCell className="text-right">{week.overlap_move_count}</TableCell>
                        <TableCell className="text-right">
                          {formatPercent(week.observed_opportunity_recall)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <div className="rounded-lg border p-4">
                <div className="mb-3 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  <h3 className="font-medium">Belangrijkste modelsignalen</h3>
                </div>
                <div className="space-y-2">
                  {status.aggregate_model_summary.feature_importance.length === 0 && (
                    <p className="text-sm text-muted-foreground">Nog geen model importance beschikbaar.</p>
                  )}
                  {status.aggregate_model_summary.feature_importance.map((feature) => (
                    <div key={feature.feature} className="flex items-center justify-between gap-3 text-sm">
                      <span className="truncate">{feature.feature}</span>
                      <Badge variant="outline">{Math.round(feature.abs_weight * 1000) / 1000}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {status.errors.length > 0 && (
              <Alert>
                <AlertTitle>Artefactmeldingen</AlertTitle>
                <AlertDescription>{status.errors[0]}</AlertDescription>
              </Alert>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
