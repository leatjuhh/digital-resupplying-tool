"use client"

import { useEffect, useState } from "react"
import { BrainCircuit, GitCompareArrows, Sparkles } from "lucide-react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { api, type ExternalAlgorithmMove, type ExternalAlgorithmProposalComparison } from "@/lib/api"

interface ExternalAlgorithmComparisonProps {
  proposalId: string
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined) {
    return "n.v.t."
  }
  return `${Math.round(value * 1000) / 10}%`
}

function MoveTable({
  title,
  moves,
  emptyLabel,
  showScore = false,
}: {
  title: string
  moves: ExternalAlgorithmMove[]
  emptyLabel: string
  showScore?: boolean
}) {
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium">{title}</h4>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Van</TableHead>
              <TableHead>Naar</TableHead>
              <TableHead>Maat</TableHead>
              <TableHead className="text-right">Aantal</TableHead>
              {showScore && <TableHead className="text-right">Score</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {moves.length === 0 && (
              <TableRow>
                <TableCell colSpan={showScore ? 5 : 4} className="text-sm text-muted-foreground">
                  {emptyLabel}
                </TableCell>
              </TableRow>
            )}
            {moves.map((move, index) => (
              <TableRow key={`${move.from_store}-${move.to_store}-${move.size}-${move.qty}-${index}`}>
                <TableCell>{move.from_store}</TableCell>
                <TableCell>{move.to_store}</TableCell>
                <TableCell>{move.size}</TableCell>
                <TableCell className="text-right">{move.qty}</TableCell>
                {showScore && <TableCell className="text-right">{move.score?.toFixed(4) ?? "-"}</TableCell>}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

export function ExternalAlgorithmComparison({ proposalId }: ExternalAlgorithmComparisonProps) {
  const [comparison, setComparison] = useState<ExternalAlgorithmProposalComparison | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchComparison() {
      try {
        setLoading(true)
        const payload = await api.externalAlgorithm.getProposalComparison(parseInt(proposalId, 10))
        setComparison(payload)
        setError(null)
      } catch (err) {
        console.error("Failed to load proposal comparison:", err)
        setError("Kon externe algoritmecontext niet laden.")
      } finally {
        setLoading(false)
      }
    }

    fetchComparison()
  }, [proposalId])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BrainCircuit className="h-5 w-5" />
          Externe Algoritmecontext
        </CardTitle>
        <CardDescription>
          Vergelijk het huidige DRT-voorstel met handmatige beslissingen en externe modelsignalen.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading && <p className="text-sm text-muted-foreground">Vergelijking laden...</p>}

        {!loading && error && (
          <Alert variant="destructive">
            <AlertTitle>Vergelijking niet beschikbaar</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {!loading && !error && comparison && !comparison.available && (
          <Alert>
            <AlertTitle>Geen match in externe weekdata</AlertTitle>
            <AlertDescription>
              Voor artikel {comparison.artikelnummer} is in de externe dataset nog geen overeenkomstige weekrecord gevonden.
            </AlertDescription>
          </Alert>
        )}

        {!loading && !error && comparison?.available && comparison.comparison && (
          <>
            <div className="flex flex-wrap gap-3">
              <Badge variant="secondary">
                Match: {comparison.comparison.year}-W{comparison.comparison.week}
              </Badge>
              <Badge variant="outline">
                DRT moves: {comparison.current_proposal.move_count}
              </Badge>
              <Badge variant="outline">
                Handmatig: {comparison.comparison.manual_observed.move_count}
              </Badge>
              <Badge variant="outline">
                Baseline: {comparison.comparison.baseline.move_count}
              </Badge>
              <Badge variant="outline">
                Model top-k: {comparison.comparison.model.selection_size}
              </Badge>
            </div>

            <div className="grid gap-4 md:grid-cols-4">
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Totale voorraad</p>
                <p className="mt-1 text-2xl font-semibold">{comparison.comparison.article_context.total_inventory}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Totale verkoop</p>
                <p className="mt-1 text-2xl font-semibold">{comparison.comparison.article_context.total_sales}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">DRT vs handmatig overlap</p>
                <p className="mt-1 text-2xl font-semibold">{comparison.comparison.drt_vs_manual.overlap_count}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Model top-k recall</p>
                <p className="mt-1 text-2xl font-semibold">
                  {formatPercent(comparison.comparison.model.top_k_recall_test)}
                </p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-lg border p-3">
                <div className="mb-2 flex items-center gap-2">
                  <GitCompareArrows className="h-4 w-4 text-muted-foreground" />
                  <p className="font-medium">DRT vs handmatig</p>
                </div>
                <p className="text-sm text-muted-foreground">
                  overlap {comparison.comparison.drt_vs_manual.overlap_count}, DRT-only{" "}
                  {comparison.comparison.drt_vs_manual.left_only_count}, manual-only{" "}
                  {comparison.comparison.drt_vs_manual.right_only_count}
                </p>
              </div>
              <div className="rounded-lg border p-3">
                <div className="mb-2 flex items-center gap-2">
                  <GitCompareArrows className="h-4 w-4 text-muted-foreground" />
                  <p className="font-medium">DRT vs baseline</p>
                </div>
                <p className="text-sm text-muted-foreground">
                  overlap {comparison.comparison.drt_vs_baseline?.overlap_count ?? 0}, DRT-only{" "}
                  {comparison.comparison.drt_vs_baseline?.left_only_count ?? 0}, baseline-only{" "}
                  {comparison.comparison.drt_vs_baseline?.right_only_count ?? 0}
                </p>
              </div>
              <div className="rounded-lg border p-3">
                <div className="mb-2 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-muted-foreground" />
                  <p className="font-medium">DRT vs model</p>
                </div>
                <p className="text-sm text-muted-foreground">
                  overlap {comparison.comparison.drt_vs_model?.overlap_count ?? 0}, DRT-only{" "}
                  {comparison.comparison.drt_vs_model?.left_only_count ?? 0}, model-only{" "}
                  {comparison.comparison.drt_vs_model?.right_only_count ?? 0}
                </p>
              </div>
            </div>

            <Tabs defaultValue="manual">
              <TabsList className="mb-4">
                <TabsTrigger value="manual">DRT vs Handmatig</TabsTrigger>
                <TabsTrigger value="model">Model hints</TabsTrigger>
                <TabsTrigger value="baseline">Baseline</TabsTrigger>
              </TabsList>

              <TabsContent value="manual" className="space-y-4">
                <MoveTable
                  title="Overlap tussen DRT en handmatig"
                  moves={comparison.comparison.drt_vs_manual.overlap_moves}
                  emptyLabel="Nog geen overlap tussen DRT en handmatige moves."
                />
                <MoveTable
                  title="Alleen in DRT voorstel"
                  moves={comparison.comparison.drt_vs_manual.left_only_moves}
                  emptyLabel="Geen DRT-only moves."
                />
                <MoveTable
                  title="Alleen handmatig gezien"
                  moves={comparison.comparison.drt_vs_manual.right_only_moves}
                  emptyLabel="Geen manual-only moves."
                />
              </TabsContent>

              <TabsContent value="model" className="space-y-4">
                <MoveTable
                  title="Model top-k suggesties"
                  moves={comparison.comparison.model.selected_moves}
                  emptyLabel="Geen modelselectie beschikbaar."
                  showScore
                />
                <MoveTable
                  title="Alleen door model gekozen"
                  moves={comparison.comparison.drt_vs_model?.right_only_moves ?? []}
                  emptyLabel="Geen model-only moves."
                  showScore
                />
              </TabsContent>

              <TabsContent value="baseline" className="space-y-4">
                <MoveTable
                  title="Baseline moves uit externe evaluatie"
                  moves={comparison.comparison.baseline.moves}
                  emptyLabel="Geen baseline_proposals beschikbaar voor dit artikel."
                />
              </TabsContent>
            </Tabs>
          </>
        )}
      </CardContent>
    </Card>
  )
}
