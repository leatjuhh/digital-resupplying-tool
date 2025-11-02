"use client"

import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { ArrowDown, ArrowUp } from "lucide-react"
import { Button } from "@/components/ui/button"

interface EditableProposalDetailProps {
  id: string
  batchId?: string
  batchInfo?: {
    totalProposals: number
    assessedProposals: number
    name: string
  }
}

export function EditableProposalDetail({ id, batchId, batchInfo }: EditableProposalDetailProps) {
  const [initialProposalData, setInitialProposalData] = useState<any>(null)
  const [proposalData, setProposalData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isBalanced, setIsBalanced] = useState(true)
  const [hasChanges, setHasChanges] = useState(false)
  const [totalDifference, setTotalDifference] = useState(0)
  const [editingBasis, setEditingBasis] = useState<'current' | 'proposed'>('current')

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
          sizes: data.sizes || [],
          stores: data.stores?.map((store: any) => ({
            id: store.id,
            name: store.name,
            inventoryCurrent: store.inventory_current || [],
            inventoryProposed: store.inventory_proposed || [],
            sold: store.sold || 0,
          })) || [],
        }
        
        setInitialProposalData(mappedData)
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

  // Calculate totals for current inventory
  const totalsCurrent = proposalData?.sizes.map((_: string, sizeIndex: number) => {
    return proposalData.stores.reduce((acc: number, store: any) => 
      acc + store.inventoryCurrent[sizeIndex], 0)
  }) || []

  // Calculate totals for proposed inventory
  const totalsProposed = proposalData?.sizes.map((_: string, sizeIndex: number) => {
    return proposalData.stores.reduce((acc: number, store: any) => 
      acc + store.inventoryProposed[sizeIndex], 0)
  }) || []

  // Calculate the total difference between current and proposed
  useEffect(() => {
    if (!proposalData || !initialProposalData) return

    let totalDiff = 0
    for (let i = 0; i < totalsCurrent.length; i++) {
      totalDiff += totalsProposed[i] - totalsCurrent[i]
    }
    setTotalDifference(totalDiff)
    setIsBalanced(totalDiff === 0)

    // Check if there are any changes
    const hasAnyChanges = proposalData.stores.some((store: any, storeIndex: number) => {
      return store.inventoryProposed.some((proposed: number, sizeIndex: number) => {
        return proposed !== initialProposalData.stores[storeIndex].inventoryProposed[sizeIndex]
      })
    })
    setHasChanges(hasAnyChanges)

    // Enable or disable the save button
    const saveButton = document.getElementById("save-button") as HTMLButtonElement
    if (saveButton) {
      saveButton.disabled = !isBalanced || !hasAnyChanges
    }

    // Dispatch custom event to share state with parent component
    const event = new CustomEvent("proposalStateChange", {
      detail: {
        isBalanced: totalDiff === 0,
        hasChanges: hasAnyChanges,
      },
    })
    window.dispatchEvent(event)
  }, [proposalData, totalsCurrent, totalsProposed, initialProposalData])

  const handleInventoryChange = (storeIndex: number, sizeIndex: number, value: string) => {
    const numValue = Number.parseInt(value) || 0

    // Update the proposed inventory
    const newProposalData = { ...proposalData }
    newProposalData.stores[storeIndex].inventoryProposed[sizeIndex] = numValue

    setProposalData(newProposalData)
  }

  // Check if there are differences between current and proposed in initial data
  const hasProposedDifferences = initialProposalData?.stores.some((store: any) => {
    return store.inventoryCurrent.some((current: number, sizeIndex: number) => {
      return current !== store.inventoryProposed[sizeIndex]
    })
  }) || false

  const loadProposalAsBase = () => {
    if (!initialProposalData) return
    
    // Start editing from proposed inventory instead of current
    setEditingBasis('proposed')
    setProposalData(initialProposalData)
    setHasChanges(false)
  }

  const resetProposal = () => {
    setProposalData(initialProposalData)
    setEditingBasis('current')
    setHasChanges(false)
  }

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

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Bewerk Herverdeling</CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={editingBasis === 'current' ? 'default' : 'secondary'}>
                Basis: {editingBasis === 'current' ? 'Huidige Voorraad' : 'AI Voorstel'}
              </Badge>
              
              {hasProposedDifferences && editingBasis === 'current' && (
                <Button variant="outline" size="sm" onClick={loadProposalAsBase}>
                  Laad AI Voorstel
                </Button>
              )}
              
              <Button variant="outline" size="sm" onClick={resetProposal} disabled={!hasChanges}>
                Resetten
              </Button>
              <Badge variant={isBalanced ? "outline" : "destructive"}>
                {isBalanced ? "Gebalanceerd" : "Ongebalanceerd"}
              </Badge>
              {hasChanges && <Badge variant="default">Gewijzigd</Badge>}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4 text-sm">
            <p>Instructies:</p>
            <ul className="list-disc pl-5 mt-2 space-y-1">
              <li>Bewerk de aantallen direct door op de getallen te klikken</li>
              <li>De totale voorraad moet gelijk blijven (gebalanceerd zijn) om op te kunnen slaan</li>
              <li>Gebruik "Laad AI Voorstel" om te starten vanaf het gegenereerde voorstel</li>
              <li>Gebruik "Resetten" om terug te gaan naar de {editingBasis === 'current' ? 'originele voorraad' : 'AI voorstel basis'}</li>
            </ul>
          </div>

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
                  {proposalData.sizes.map((_: string, sizeIndex: number) => {
                    const currentTotal = totalsCurrent[sizeIndex]
                    const proposedTotal = totalsProposed[sizeIndex]
                    const diff = proposedTotal - currentTotal
                    const hasImbalance = diff !== 0

                    return (
                      <TableCell
                        key={sizeIndex}
                        className={`text-center ${hasImbalance ? "bg-red-100 dark:bg-red-900/20" : ""}`}
                      >
                        <div className="flex flex-col items-center">
                          <span>{proposedTotal}</span>
                          {diff !== 0 && (
                            <span className={`text-xs ${diff > 0 ? "text-green-500" : "text-red-500"}`}>
                              {diff > 0 ? `+${diff}` : diff}
                            </span>
                          )}
                        </div>
                      </TableCell>
                    )
                  })}
                  <TableCell className="text-center">
                    {proposalData.stores.reduce((acc: number, store: any) => acc + store.sold, 0)}
                  </TableCell>
                </TableRow>
                {proposalData.stores.map((store: any, storeIndex: number) => {
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
                      {store.inventoryProposed.map((qty: number, sizeIndex: number) => {
                        const current = store.inventoryCurrent[sizeIndex]
                        const diff = qty - current

                        return (
                          <TableCell
                            key={sizeIndex}
                            className={`text-center p-2 ${diff !== 0 ? "bg-blue-100 dark:bg-blue-900/20" : ""}`}
                          >
                            <div className="relative flex flex-col items-center">
                              <Input
                                type="number"
                                value={qty}
                                onChange={(e) => handleInventoryChange(storeIndex, sizeIndex, e.target.value)}
                                className="w-12 h-8 text-center p-0"
                                min="0"
                              />
                              {diff !== 0 && (
                                <span
                                  className={`absolute -bottom-4 text-xs ${diff > 0 ? "text-green-500" : "text-red-500"}`}
                                >
                                  {diff > 0 ? (
                                    <ArrowUp className="h-3 w-3 inline" />
                                  ) : (
                                    <ArrowDown className="h-3 w-3 inline" />
                                  )}
                                  {Math.abs(diff)}
                                </span>
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

          <div className="mt-6 text-sm text-muted-foreground">
            <p>Legenda:</p>
            <div className="flex items-center gap-4 mt-1">
              <div className="flex items-center">
                <div className="h-4 w-4 bg-blue-100 dark:bg-blue-900/20 mr-2"></div>
                <span>Gewijzigde voorraad</span>
              </div>
              <div className="flex items-center">
                <ArrowUp className="h-4 w-4 text-green-500 mr-1" />
                <span>Toegevoegd</span>
              </div>
              <div className="flex items-center">
                <ArrowDown className="h-4 w-4 text-red-500 mr-1" />
                <span>Verwijderd</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
