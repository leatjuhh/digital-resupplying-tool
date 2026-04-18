"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { CheckCircle2 } from "lucide-react"
import { ExternalAlgorithmComparison } from "@/components/proposals/external-algorithm-comparison"

interface ProposalDetailProps {
  id: string
  batchId?: string
  batchInfo?: {
    totalProposals: number
    assessedProposals: number
    name: string
  }
}

// "169 D Blouse diversen Artikelgroep : 0" → "169 D Blouse diversen"
function parseHoofdgroep(raw: string): string {
  return raw.replace(/\s*Artikelgroep\s*:\s*\S+.*$/i, '').trim()
}

// "2026 Collectie : 11 Voorjaar Nakoop Bestelcode : E2 26-033 Jade1073"
function parseSeizoenjaarInfo(raw: string) {
  const yearMatch = raw.match(/^(\d{4})/)
  const collectieMatch = raw.match(/Collectie\s*:\s*(.*?)(?:\s*Bestelcode|$)/i)
  const bestelcodeMatch = raw.match(/Bestelcode\s*:\s*(.+)$/i)
  return {
    seizoenjaar: yearMatch?.[1] ?? raw,
    collectie: collectieMatch?.[1]?.trim() ?? '',
    bestelcode: bestelcodeMatch?.[1]?.trim() ?? '',
  }
}

function getColorSwatch(kleur: string): string {
  const lower = kleur.toLowerCase()
  if (lower.includes('dark brown') || lower.includes('donkerbruin')) return '#6b3a2a'
  if (lower.includes('brown') || lower.includes('bruin')) return '#92400e'
  if (lower.includes('pink') || lower.includes('roze')) return '#f9a8d4'
  if (lower.includes('blue') || lower.includes('blauw')) return '#93c5fd'
  if (lower.includes('red') || lower.includes('rood')) return '#fca5a5'
  if (lower.includes('green') || lower.includes('groen')) return '#86efac'
  if (lower.includes('yellow') || lower.includes('geel')) return '#fde047'
  if (lower.includes('black') || lower.includes('zwart')) return '#374151'
  if (lower.includes('white') || lower.includes('wit')) return '#e5e7eb'
  if (lower.includes('grey') || lower.includes('gray') || lower.includes('grijs')) return '#9ca3af'
  if (lower.includes('beige') || lower.includes('camel')) return '#d4b896'
  return '#cccccc'
}

function MetaField({ label, value, children }: { label: string; value?: string; children?: React.ReactNode }) {
  return (
    <div className="flex gap-1 items-baseline min-w-0">
      <span className="text-xs text-muted-foreground whitespace-nowrap shrink-0">{label}:</span>
      {children ?? <span className="text-xs font-medium truncate">{value ?? "—"}</span>}
    </div>
  )
}

export function ProposalDetail({ id, batchId, batchInfo }: ProposalDetailProps) {
  const [proposalData, setProposalData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchProposalData() {
      try {
        setLoading(true)
        const data = await api.proposals.getByIdFull(parseInt(id))

        const rawHoofdgroep = data.metadata?.Hoofdgroep || ''
        const rawSeizoenjaar = data.metadata?.Seizoenjaar || ''
        const seizoenjaarInfo = parseSeizoenjaarInfo(rawSeizoenjaar)

        // Bestelcode: try dedicated key first, then parsed from Seizoenjaar, then artikelnummer
        const bestelcode =
          data.metadata?.Bestelcode ||
          seizoenjaarInfo.bestelcode ||
          data.artikelnummer

        const mappedData = {
          id,
          volgnummer: data.metadata?.Volgnummer || data.artikelnummer,
          articleCode: data.artikelnummer,
          description: data.metadata?.Omschrijving || data.article_name || 'Onbekend',
          isOptimalDistribution: Boolean(data.is_optimal_distribution),
          optimalDistributionReason: data.optimal_distribution_reason || '',
          leverancier: data.metadata?.Leverancier || '',
          kleur: data.metadata?.Kleur || '',
          hoofdgroep: rawHoofdgroep ? parseHoofdgroep(rawHoofdgroep) : '',
          seizoenjaar: seizoenjaarInfo.seizoenjaar,
          collectie: data.metadata?.Collectie || seizoenjaarInfo.collectie,
          collectiecode: data.metadata?.Collectiecode || '',
          bestelcode,
          moves: data.moves || [],
          sizes: data.sizes || [],
          stores: data.stores?.map((store: any) => ({
            id: store.id,
            name: store.name,
            inventoryCurrent: store.inventory_current || [],
            inventoryProposed: store.inventory_proposed || [],
            sold: store.sold || 0,
          })) || [],
        }

        setProposalData(mappedData)
        setError(null)
      } catch (err) {
        console.error('Failed to fetch proposal:', err)
        setError('Kon voorstel niet ophalen')
      } finally {
        setLoading(false)
      }
    }

    fetchProposalData()
  }, [id])

  if (loading) {
    return (
      <div className="grid gap-4 mt-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">Laden...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !proposalData) {
    return (
      <div className="grid gap-4 mt-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-destructive">{error || 'Geen data beschikbaar'}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const totals = proposalData.sizes.map((_: string, sizeIndex: number) =>
    proposalData.stores.reduce((acc: number, store: any) => acc + store.inventoryCurrent[sizeIndex], 0)
  )
  const totalSold = proposalData.stores.reduce((acc: number, store: any) => acc + store.sold, 0)
  const totalsProposed = proposalData.sizes.map((_: string, sizeIndex: number) =>
    proposalData.stores.reduce((acc: number, store: any) => acc + store.inventoryProposed[sizeIndex], 0)
  )

  const hasDifferences = proposalData.stores.some((store: any) =>
    store.inventoryCurrent.some((current: number, i: number) => current !== store.inventoryProposed[i])
  )
  const hasNoChanges = proposalData.isOptimalDistribution || (!hasDifferences && proposalData.stores.length > 0)

  const showBatchProgress = batchInfo && batchInfo.totalProposals > 0
  const progressPercentage = showBatchProgress
    ? Math.round((batchInfo.assessedProposals / batchInfo.totalProposals) * 100)
    : 0

  const collectieDisplay = proposalData.collectiecode
    ? `${proposalData.collectiecode} ${proposalData.collectie}`.trim()
    : proposalData.collectie

  return (
    <div className="grid gap-4 mt-2">
      {showBatchProgress && (
        <Card>
          <CardContent className="pt-4 pb-4">
            <div className="flex flex-col space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">Reeks: {batchInfo.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    Voorstel {batchInfo.assessedProposals + 1} van {batchInfo.totalProposals}
                  </p>
                </div>
                <Badge variant="outline">Voortgang: {progressPercentage}%</Badge>
              </div>
              <Progress value={progressPercentage} className="h-2 w-full relative">
                <div
                  className="progress-bar-inner absolute top-0 left-0 h-full bg-blue-500 rounded-full"
                  style={{ width: `${progressPercentage}%` }}
                />
              </Progress>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── VOORSTEL TAB ─────────────────────────────────────────────── */}
      <TabsContent value="voorstel" className="mt-0 grid gap-4">

        {/* Compacte artikel-header — spiegelt blauwe sectie uit PDF */}
        <div className="rounded-md border bg-muted/30 px-4 py-2.5">
          <div className="grid gap-x-8 gap-y-1 md:grid-cols-3">
            {/* Kolom 1: Volgnummer, Omschrijving, Seizoenjaar */}
            <div className="space-y-1">
              <MetaField label="Volgnummer" value={proposalData.volgnummer} />
              <MetaField label="Omschrijving" value={proposalData.description} />
              <MetaField label="Seizoenjaar" value={proposalData.seizoenjaar} />
            </div>
            {/* Kolom 2: Leverancier, Hoofdgroep, Collectie */}
            <div className="space-y-1">
              <MetaField label="Leverancier" value={proposalData.leverancier || "—"} />
              <MetaField label="Hoofdgroep" value={proposalData.hoofdgroep || "—"} />
              <MetaField label="Collectie" value={collectieDisplay || "—"} />
            </div>
            {/* Kolom 3: Kleur, Bestelcode */}
            <div className="space-y-1">
              <MetaField label="Kleur">
                <span className="flex items-center gap-1.5 text-xs font-medium">
                  {proposalData.kleur || "—"}
                  {proposalData.kleur && (
                    <span
                      className="inline-block h-3 w-3 rounded-full border shrink-0"
                      style={{ backgroundColor: getColorSwatch(proposalData.kleur) }}
                    />
                  )}
                </span>
              </MetaField>
              <MetaField label="Bestelcode" value={proposalData.bestelcode || "—"} />
            </div>
          </div>
        </div>

        {/* Interfiliaalverdeling */}
        <Card>
          <CardHeader className="pb-2 pt-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Interfiliaalverdeling</CardTitle>
              <div className="flex gap-2">
                {hasDifferences && <Badge>Wijzigingen voorgesteld</Badge>}
                {hasNoChanges && (
                  <Badge variant="secondary">
                    <CheckCircle2 className="mr-1 h-3 w-3" />Optimaal Verdeeld
                  </Badge>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            {hasNoChanges && (
              <Alert className="mb-3 border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950">
                <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                <AlertTitle className="text-green-800 dark:text-green-300">Optimaal Verdeeld</AlertTitle>
                <AlertDescription className="text-green-700 dark:text-green-400">
                  {proposalData.optimalDistributionReason ||
                    "Dit artikel is reeds optimaal verdeeld over de filialen. Het herverdelingsalgoritme heeft geen verbeteringen gevonden."}
                </AlertDescription>
              </Alert>
            )}

            <Tabs defaultValue="comparison">
              <TabsList className="mb-3">
                <TabsTrigger value="comparison">Vergelijking</TabsTrigger>
                <TabsTrigger value="current">Huidige Situatie</TabsTrigger>
                {hasDifferences && <TabsTrigger value="proposed">Voorgestelde Situatie</TabsTrigger>}
              </TabsList>

              <TabsContent value="comparison">
                <div className="rounded-md border overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[120px] font-bold">Filiaal</TableHead>
                        {proposalData.sizes.map((size: string) => (
                          <TableHead key={size} className="text-center min-w-[50px]">{size}</TableHead>
                        ))}
                        <TableHead className="text-center font-bold">Verkocht</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="font-bold bg-muted/50">
                        <TableCell>Totaal</TableCell>
                        {totals.map((total: number, i: number) => (
                          <TableCell key={i} className="text-center">{total}</TableCell>
                        ))}
                        <TableCell className="text-center">{totalSold}</TableCell>
                      </TableRow>
                      {proposalData.stores.map((store: any) => {
                        const hasInventory =
                          store.inventoryCurrent.some((val: number) => val > 0) ||
                          store.inventoryProposed.some((val: number) => val > 0) ||
                          store.sold > 0
                        if (!hasInventory && store.id !== "0") return null
                        return (
                          <TableRow key={store.id}>
                            <TableCell>{store.id} {store.name}</TableCell>
                            {store.inventoryCurrent.map((qty: number, i: number) => {
                              const proposed = store.inventoryProposed[i]
                              const hasDiff = qty !== proposed
                              return (
                                <TableCell key={i} className="text-center p-0">
                                  <div className="grid grid-cols-1">
                                    <div className={`py-2 ${hasDiff ? "bg-green-100 dark:bg-green-900/20" : ""}`}>
                                      {qty > 0 ? qty : "."}
                                    </div>
                                    {hasDiff && (
                                      <div className="py-2 bg-blue-100 dark:bg-blue-900/20 border-t">
                                        {proposed > 0 ? proposed : "."}
                                      </div>
                                    )}
                                  </div>
                                </TableCell>
                              )
                            })}
                            <TableCell className="text-center">{store.sold > 0 ? store.sold : "."}</TableCell>
                          </TableRow>
                        )
                      })}
                    </TableBody>
                  </Table>
                </div>
                <div className="mt-2 text-xs text-muted-foreground flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <div className="h-3 w-3 bg-green-100 dark:bg-green-900/20 border" />
                    <span>Huidige voorraad</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="h-3 w-3 bg-blue-100 dark:bg-blue-900/20 border" />
                    <span>Voorgestelde voorraad (bij wijziging)</span>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="current">
                <div className="rounded-md border overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[120px] font-bold">Filiaal</TableHead>
                        {proposalData.sizes.map((size: string) => (
                          <TableHead key={size} className="text-center min-w-[50px]">{size}</TableHead>
                        ))}
                        <TableHead className="text-center font-bold">Verkocht</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="font-bold bg-muted/50">
                        <TableCell>Totaal</TableCell>
                        {totals.map((total: number, i: number) => (
                          <TableCell key={i} className="text-center">{total}</TableCell>
                        ))}
                        <TableCell className="text-center">{totalSold}</TableCell>
                      </TableRow>
                      {proposalData.stores.map((store: any) => {
                        const hasInventory = store.inventoryCurrent.some((val: number) => val > 0) || store.sold > 0
                        if (!hasInventory && store.id !== "0") return null
                        return (
                          <TableRow key={store.id}>
                            <TableCell>{store.id} {store.name}</TableCell>
                            {store.inventoryCurrent.map((qty: number, i: number) => (
                              <TableCell key={i} className="text-center">{qty > 0 ? qty : "."}</TableCell>
                            ))}
                            <TableCell className="text-center">{store.sold > 0 ? store.sold : "."}</TableCell>
                          </TableRow>
                        )
                      })}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>

              <TabsContent value="proposed">
                <div className="rounded-md border overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[120px] font-bold">Filiaal</TableHead>
                        {proposalData.sizes.map((size: string) => (
                          <TableHead key={size} className="text-center min-w-[50px]">{size}</TableHead>
                        ))}
                        <TableHead className="text-center font-bold">Verkocht</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="font-bold bg-muted/50">
                        <TableCell>Totaal</TableCell>
                        {totalsProposed.map((total: number, i: number) => (
                          <TableCell key={i} className="text-center">{total}</TableCell>
                        ))}
                        <TableCell className="text-center">{totalSold}</TableCell>
                      </TableRow>
                      {proposalData.stores.map((store: any) => {
                        const hasInventory = store.inventoryProposed.some((val: number) => val > 0) || store.sold > 0
                        if (!hasInventory && store.id !== "0") return null
                        return (
                          <TableRow key={store.id}>
                            <TableCell>{store.id} {store.name}</TableCell>
                            {store.inventoryProposed.map((qty: number, i: number) => {
                              const current = store.inventoryCurrent[i]
                              const hasDiff = qty !== current
                              return (
                                <TableCell key={i} className={`text-center ${hasDiff ? "bg-blue-100 dark:bg-blue-900/20" : ""}`}>
                                  {qty > 0 ? qty : "."}
                                </TableCell>
                              )
                            })}
                            <TableCell className="text-center">{store.sold > 0 ? store.sold : "."}</TableCell>
                          </TableRow>
                        )
                      })}
                    </TableBody>
                  </Table>
                </div>
                <div className="mt-2 text-xs text-muted-foreground flex items-center gap-1">
                  <div className="h-3 w-3 bg-blue-100 dark:bg-blue-900/20 border" />
                  <span>Gewijzigde voorraad</span>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </TabsContent>

      {/* ── ANALYSE TAB ──────────────────────────────────────────────── */}
      <TabsContent value="analyse" className="mt-0 grid gap-4">
        <ExternalAlgorithmComparison proposalId={id} />

        {proposalData.moves && proposalData.moves.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Geplande moves ({proposalData.moves.length})</CardTitle>
                {proposalData.moves.some((m: any) => m.model_score !== null && m.model_score !== undefined) && (
                  <Badge variant="outline" className="text-xs font-normal">
                    🤖 Model-scores actief (shadow)
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Van</TableHead>
                      <TableHead>Naar</TableHead>
                      <TableHead className="text-center">Maat</TableHead>
                      <TableHead className="text-center">Aantal</TableHead>
                      <TableHead className="text-center">Demand</TableHead>
                      <TableHead className="text-center">Model</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {proposalData.moves.map((move: any, idx: number) => {
                      const demandScore = move.score ?? null
                      const modelScore = move.model_score ?? null
                      return (
                        <TableRow key={idx}>
                          <TableCell className="text-sm">{move.from_store_name || move.from_store}</TableCell>
                          <TableCell className="text-sm">{move.to_store_name || move.to_store}</TableCell>
                          <TableCell className="text-center font-mono text-sm">{move.size}</TableCell>
                          <TableCell className="text-center">{move.qty}</TableCell>
                          <TableCell className="text-center">
                            {demandScore !== null ? (
                              <Badge variant="secondary" className={`text-xs tabular-nums ${demandScore >= 0.7 ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : demandScore >= 0.4 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}>
                                {demandScore.toFixed(2)}
                              </Badge>
                            ) : <span className="text-muted-foreground text-xs">—</span>}
                          </TableCell>
                          <TableCell className="text-center">
                            {modelScore !== null ? (
                              <Badge variant="outline" className={`text-xs tabular-nums ${modelScore >= 0.7 ? 'border-green-400 text-green-700 dark:text-green-400' : modelScore >= 0.4 ? 'border-yellow-400 text-yellow-700 dark:text-yellow-400' : 'border-red-400 text-red-700 dark:text-red-400'}`}>
                                {modelScore.toFixed(2)}
                              </Badge>
                            ) : <span className="text-muted-foreground text-xs">—</span>}
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </div>
              <p className="px-4 pb-3 pt-2 text-xs text-muted-foreground">
                Demand = algoritme-score (0–1). Model = ML-score (0–1, shadow mode). Groen ≥ 0.7 · Geel 0.4–0.7 · Rood &lt; 0.4
              </p>
            </CardContent>
          </Card>
        )}
      </TabsContent>
    </div>
  )
}
