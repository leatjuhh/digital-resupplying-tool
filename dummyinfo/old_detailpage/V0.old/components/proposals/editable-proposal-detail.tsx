"use client"

import { useState, useEffect } from "react"
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
  // Sample data based on the PDF example
  const initialProposalData = {
    id,
    articleCode: "TC039-04",
    description: "Brisia Peacock Top",
    supplier: {
      id: "70",
      name: "NED",
    },
    color: {
      id: "32",
      name: "pink",
    },
    category: {
      id: "149",
      name: "D T-Shirt Diversen",
    },
    subcategory: {
      id: "0",
      name: "",
    },
    seasonYear: "2025",
    collection: {
      id: "10",
      name: "Voorjaar Voorkoop",
    },
    orderCode: "TC039-04 Brisia475",
    lastDeliveryDate: "",
    totalSold: 14,
    sizes: ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"],
    stores: [
      {
        id: "0",
        name: "Centraal M",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
      {
        id: "2",
        name: "Lumitex",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
      {
        id: "3",
        name: "Mag Part.",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
      {
        id: "5",
        name: "Panningen",
        inventoryCurrent: [0, 0, 1, 1, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 1, 0, 0, 0, 0, 0],
        sold: 6,
      },
      {
        id: "6",
        name: "Echt",
        inventoryCurrent: [0, 0, 0, 1, 1, 1, 1, 0],
        inventoryProposed: [0, 0, 0, 1, 1, 1, 1, 0],
        sold: 1,
      },
      {
        id: "8",
        name: "Weert",
        inventoryCurrent: [0, 0, 1, 1, 1, 0, 1, 0],
        inventoryProposed: [0, 0, 1, 1, 1, 0, 1, 0],
        sold: 1,
      },
      {
        id: "9",
        name: "Stein",
        inventoryCurrent: [0, 0, 1, 2, 1, 1, 0, 0],
        inventoryProposed: [0, 0, 1, 2, 1, 1, 0, 0],
        sold: 0,
      },
      {
        id: "11",
        name: "Brunssum",
        inventoryCurrent: [0, 0, 0, 1, 1, 1, 1, 0],
        inventoryProposed: [0, 0, 0, 1, 1, 1, 1, 0],
        sold: 1,
      },
      {
        id: "12",
        name: "Kerkrade",
        inventoryCurrent: [0, 0, 0, 1, 1, 2, 1, 0],
        inventoryProposed: [0, 0, 0, 1, 1, 2, 1, 0],
        sold: 1,
      },
      {
        id: "13",
        name: "Budel",
        inventoryCurrent: [0, 0, 1, 2, 1, 1, 0, 0],
        inventoryProposed: [0, 0, 1, 2, 1, 1, 0, 0],
        sold: 0,
      },
      {
        id: "14",
        name: "OL Weert",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
      {
        id: "15",
        name: "OL Sittard",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
      {
        id: "16",
        name: "OL Roermon",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
      {
        id: "27",
        name: "Klachten",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
      {
        id: "31",
        name: "Tilburg",
        inventoryCurrent: [0, 0, 0, 1, 1, 1, 1, 0],
        inventoryProposed: [0, 0, 0, 1, 1, 1, 1, 0],
        sold: 1,
      },
      {
        id: "35",
        name: "Etten-Leur",
        inventoryCurrent: [0, 0, 1, 1, 1, 1, 0, 0],
        inventoryProposed: [0, 0, 1, 2, 1, 1, 0, 0],
        sold: 2,
      },
      {
        id: "38",
        name: "Tegelen",
        inventoryCurrent: [0, 0, 1, 1, 1, 0, 0, 0],
        inventoryProposed: [0, 0, 1, 1, 1, 0, 0, 0],
        sold: 1,
      },
      {
        id: "39",
        name: "OL Blerick",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
    ],
  }

  const [proposalData, setProposalData] = useState(initialProposalData)
  const [isBalanced, setIsBalanced] = useState(true)
  const [hasChanges, setHasChanges] = useState(false)
  const [totalDifference, setTotalDifference] = useState(0)

  // Calculate totals for current inventory
  const totalsCurrent = proposalData.sizes.map((_, sizeIndex) => {
    return proposalData.stores.reduce((acc, store) => acc + store.inventoryCurrent[sizeIndex], 0)
  })

  // Calculate totals for proposed inventory
  const totalsProposed = proposalData.sizes.map((_, sizeIndex) => {
    return proposalData.stores.reduce((acc, store) => acc + store.inventoryProposed[sizeIndex], 0)
  })

  // Calculate the total difference between current and proposed
  useEffect(() => {
    let totalDiff = 0
    for (let i = 0; i < totalsCurrent.length; i++) {
      totalDiff += totalsProposed[i] - totalsCurrent[i]
    }
    setTotalDifference(totalDiff)
    setIsBalanced(totalDiff === 0)

    // Check if there are any changes
    const hasAnyChanges = proposalData.stores.some((store, storeIndex) => {
      return store.inventoryProposed.some((proposed, sizeIndex) => {
        return proposed !== initialProposalData.stores[storeIndex].inventoryProposed[sizeIndex]
      })
    })
    setHasChanges(hasAnyChanges)

    // Enable or disable the save button
    const saveButton = document.getElementById("save-button") as HTMLButtonElement
    if (saveButton) {
      saveButton.disabled = !isBalanced || !hasChanges
    }

    // Dispatch custom event to share state with parent component
    const event = new CustomEvent("proposalStateChange", {
      detail: {
        isBalanced: totalDiff === 0,
        hasChanges: hasAnyChanges,
      },
    })
    window.dispatchEvent(event)
  }, [proposalData, totalsCurrent, totalsProposed, initialProposalData.stores])

  const handleInventoryChange = (storeIndex: number, sizeIndex: number, value: string) => {
    const numValue = Number.parseInt(value) || 0

    // Update the proposed inventory
    const newProposalData = { ...proposalData }
    newProposalData.stores[storeIndex].inventoryProposed[sizeIndex] = numValue

    setProposalData(newProposalData)
  }

  const resetProposal = () => {
    setProposalData(initialProposalData)
    setHasChanges(false)
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
                  style={{ backgroundColor: proposalData.color.name === "pink" ? "#f9a8d4" : "#cccccc" }}
                />
              </div>
              <p className="text-sm">
                Leverancier: {proposalData.supplier.name} ({proposalData.supplier.id})
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
              <Button variant="outline" size="sm" onClick={resetProposal} disabled={!hasChanges}>
                Resetten naar origineel
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
              <li>Gebruik de "Resetten naar origineel" knop om alle wijzigingen ongedaan te maken</li>
            </ul>
          </div>

          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[120px] font-bold">Filiaal</TableHead>
                  {proposalData.sizes.map((size, i) => (
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
                  {proposalData.sizes.map((_, sizeIndex) => {
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
                    {proposalData.stores.reduce((acc, store) => acc + store.sold, 0)}
                  </TableCell>
                </TableRow>
                {proposalData.stores.map((store, storeIndex) => {
                  // Skip rows with all zeros
                  const hasInventory =
                    store.inventoryCurrent.some((val) => val > 0) ||
                    store.inventoryProposed.some((val) => val > 0) ||
                    store.sold > 0
                  if (!hasInventory && store.id !== "0") return null

                  return (
                    <TableRow key={store.id}>
                      <TableCell>
                        {store.id} {store.name}
                      </TableCell>
                      {store.inventoryProposed.map((qty, sizeIndex) => {
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
