"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, CheckCircle2 } from "lucide-react"
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

export function ProposalDetail({ id, batchId, batchInfo }: ProposalDetailProps) {
  const [proposalData, setProposalData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchProposalData() {
      try {
        setLoading(true)
        const data = await api.proposals.getByIdFull(parseInt(id))
        
        // Map API response to V0 structure
        const mappedData = {
          id,
          articleCode: data.artikelnummer,
          description: data.article_name || 'Onbekend',
          proposalReason: data.reason || '',
          appliedRules: data.applied_rules || [],
          isOptimalDistribution: Boolean(data.is_optimal_distribution),
          optimalDistributionReason: data.optimal_distribution_reason || '',
          supplier: {
            id: data.metadata?.Leverancier || '',
            name: data.metadata?.Leverancier || 'Onbekend',
          },
          color: {
            id: data.metadata?.Kleur || '',
            name: data.metadata?.Kleur || 'Onbekend',
          },
          category: {
            id: data.metadata?.Categorie || '',
            name: data.metadata?.Categorie || 'Onbekend',
          },
          subcategory: {
            id: '',
            name: '',
          },
          seasonYear: data.metadata?.Seizoenjaar || 'Onbekend',
          collection: {
            id: data.metadata?.Collectiecode || '',
            name: data.metadata?.Collectie || 'Onbekend',
          },
          orderCode: data.metadata?.Bestelcode || data.artikelnummer,
          lastDeliveryDate: '',
          totalSold: data.stores?.reduce((acc: number, store: any) => acc + store.sold, 0) || 0,
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
      <div className="grid gap-6">
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
      <div className="grid gap-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-destructive">{error || 'Geen data beschikbaar'}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Calculate totals for each size
  const totals = proposalData.sizes.map((_: string, sizeIndex: number) => {
    return proposalData.stores.reduce((acc: number, store: any) => 
      acc + store.inventoryCurrent[sizeIndex], 0)
  })

  const totalSold = proposalData.stores.reduce((acc: number, store: any) => 
    acc + store.sold, 0)

  // Calculate totals for proposed
  const totalsProposed = proposalData.sizes.map((_: string, sizeIndex: number) => {
    return proposalData.stores.reduce((acc: number, store: any) => 
      acc + store.inventoryProposed[sizeIndex], 0)
  })

  // Find differences between current and proposed
  const hasDifferences = proposalData.stores.some((store: any) => {
    return store.inventoryCurrent.some((current: number, sizeIndex: number) => {
      return current !== store.inventoryProposed[sizeIndex]
    })
  })

  // Prefer expliciete backend-status voor optimale verdeling.
  const hasNoChanges = proposalData.isOptimalDistribution || (!hasDifferences && proposalData.stores.length > 0)

  const showBatchProgress = batchInfo && batchInfo.totalProposals > 0
  const progressPercentage = showBatchProgress
    ? Math.round((batchInfo.assessedProposals / batchInfo.totalProposals) * 100)
    : 0

  return (
    <div className="grid gap-6">
      {showBatchProgress && (
        <Card>
          <CardContent className="pt-6">
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
                ></div>
              </Progress>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-xl">Artikel Informatie</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Artikel</h3>
              <p className="font-medium">{proposalData.description}</p>
              <p className="text-sm">Code: {proposalData.articleCode}</p>
              <p className="text-sm">Bestelcode: {proposalData.orderCode}</p>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Collectie</h3>
              <p className="font-medium">{proposalData.collection.name}</p>
              <p className="text-sm">Seizoen: {proposalData.seasonYear}</p>
              <p className="text-sm">Collectiecode: {proposalData.collection.id}</p>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Details</h3>
              <div className="flex items-center gap-2">
                <p className="font-medium">Kleur: {proposalData.color.name}</p>
                <div
                  className="h-4 w-4 rounded-full border"
                  style={{ 
                    backgroundColor: proposalData.color.name === "pink" ? "#f9a8d4" : 
                                    proposalData.color.name === "blue" ? "#93c5fd" :
                                    proposalData.color.name === "red" ? "#fca5a5" :
                                    proposalData.color.name === "green" ? "#86efac" :
                                    proposalData.color.name === "yellow" ? "#fde047" :
                                    "#cccccc" 
                  }}
                />
              </div>
              <p className="text-sm">
                Leverancier: {proposalData.supplier.name} {proposalData.supplier.id && `(${proposalData.supplier.id})`}
              </p>
              <p className="text-sm">Categorie: {proposalData.category.name}</p>
            </div>
          </div>
        </CardContent>
      </Card>

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
                        <TableCell className="text-sm">
                          {move.from_store_name || move.from_store}
                        </TableCell>
                        <TableCell className="text-sm">
                          {move.to_store_name || move.to_store}
                        </TableCell>
                        <TableCell className="text-center font-mono text-sm">{move.size}</TableCell>
                        <TableCell className="text-center">{move.qty}</TableCell>
                        <TableCell className="text-center">
                          {demandScore !== null ? (
                            <Badge
                              variant="secondary"
                              className={`text-xs tabular-nums ${demandScore >= 0.7 ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : demandScore >= 0.4 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}
                            >
                              {demandScore.toFixed(2)}
                            </Badge>
                          ) : <span className="text-muted-foreground text-xs">—</span>}
                        </TableCell>
                        <TableCell className="text-center">
                          {modelScore !== null ? (
                            <Badge
                              variant="outline"
                              className={`text-xs tabular-nums ${modelScore >= 0.7 ? 'border-green-400 text-green-700 dark:text-green-400' : modelScore >= 0.4 ? 'border-yellow-400 text-yellow-700 dark:text-yellow-400' : 'border-red-400 text-red-700 dark:text-red-400'}`}
                            >
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

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Interfiliaalverdeling</CardTitle>
            {hasDifferences && <Badge className="ml-2">Wijzigingen voorgesteld</Badge>}
            {hasNoChanges && <Badge variant="secondary" className="ml-2"><CheckCircle2 className="mr-1 h-3 w-3" />Optimaal Verdeeld</Badge>}
          </div>
        </CardHeader>
        <CardContent>
          {hasNoChanges && (
            <Alert className="mb-4 border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950">
              <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
              <AlertTitle className="text-green-800 dark:text-green-300">Optimaal Verdeeld</AlertTitle>
              <AlertDescription className="text-green-700 dark:text-green-400">
                {proposalData.optimalDistributionReason ||
                  "Dit artikel is reeds optimaal verdeeld over de filialen. Het herverdelingsalgoritme heeft geen verbeteringen gevonden."}
              </AlertDescription>
            </Alert>
          )}
          
          <Tabs defaultValue="comparison">
            <TabsList className="mb-4">
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
                        <TableHead key={size} className="text-center min-w-[50px]">
                          {size}
                        </TableHead>
                      ))}
                      <TableHead className="text-center font-bold">Verkocht</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="font-bold bg-muted/50">
                      <TableCell>Totaal</TableCell>
                      {totals.map((total: number, i: number) => (
                        <TableCell key={i} className="text-center">
                          {total}
                        </TableCell>
                      ))}
                      <TableCell className="text-center">{totalSold}</TableCell>
                    </TableRow>
                    {proposalData.stores.map((store: any) => {
                      // Skip rows with all zeros
                      const hasInventory =
                        store.inventoryCurrent.some((val: number) => val > 0) ||
                        store.inventoryProposed.some((val: number) => val > 0) ||
                        store.sold > 0
                      if (!hasInventory && store.id !== "0") return null

                      return (
                        <TableRow key={store.id}>
                          <TableCell>
                            {store.id} {store.name}
                          </TableCell>
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
              <div className="mt-3 text-sm text-muted-foreground">
                <p>Legenda:</p>
                <div className="flex items-center gap-4 mt-1">
                  <div className="flex items-center">
                    <div className="h-4 w-4 bg-green-100 dark:bg-green-900/20 mr-2"></div>
                    <span>Huidige voorraad</span>
                  </div>
                  <div className="flex items-center">
                    <div className="h-4 w-4 bg-blue-100 dark:bg-blue-900/20 mr-2"></div>
                    <span>Voorgestelde voorraad (bij wijziging)</span>
                  </div>
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
                        <TableHead key={size} className="text-center min-w-[50px]">
                          {size}
                        </TableHead>
                      ))}
                      <TableHead className="text-center font-bold">Verkocht</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="font-bold bg-muted/50">
                      <TableCell>Totaal</TableCell>
                      {totals.map((total: number, i: number) => (
                        <TableCell key={i} className="text-center">
                          {total}
                        </TableCell>
                      ))}
                      <TableCell className="text-center">{totalSold}</TableCell>
                    </TableRow>
                    {proposalData.stores.map((store: any) => {
                      // Skip rows with all zeros
                      const hasInventory = store.inventoryCurrent.some((val: number) => val > 0) || store.sold > 0
                      if (!hasInventory && store.id !== "0") return null

                      return (
                        <TableRow key={store.id}>
                          <TableCell>
                            {store.id} {store.name}
                          </TableCell>
                          {store.inventoryCurrent.map((qty: number, i: number) => (
                            <TableCell key={i} className="text-center">
                              {qty > 0 ? qty : "."}
                            </TableCell>
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
                        <TableHead key={size} className="text-center min-w-[50px]">
                          {size}
                        </TableHead>
                      ))}
                      <TableHead className="text-center font-bold">Verkocht</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow className="font-bold bg-muted/50">
                      <TableCell>Totaal</TableCell>
                      {totalsProposed.map((total: number, i: number) => (
                        <TableCell key={i} className="text-center">
                          {total}
                        </TableCell>
                      ))}
                      <TableCell className="text-center">{totalSold}</TableCell>
                    </TableRow>
                    {proposalData.stores.map((store: any) => {
                      // Skip rows with all zeros
                      const hasInventory = store.inventoryProposed.some((val: number) => val > 0) || store.sold > 0
                      if (!hasInventory && store.id !== "0") return null

                      return (
                        <TableRow key={store.id}>
                          <TableCell>
                            {store.id} {store.name}
                          </TableCell>
                          {store.inventoryProposed.map((qty: number, i: number) => {
                            const current = store.inventoryCurrent[i]
                            const hasDiff = qty !== current

                            return (
                              <TableCell
                                key={i}
                                className={`text-center ${hasDiff ? "bg-blue-100 dark:bg-blue-900/20" : ""}`}
                              >
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
              <div className="mt-3 text-sm text-muted-foreground">
                <p>Legenda:</p>
                <div className="flex items-center mt-1">
                  <div className="h-4 w-4 bg-blue-100 dark:bg-blue-900/20 mr-2"></div>
                  <span>Gewijzigde voorraad</span>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
