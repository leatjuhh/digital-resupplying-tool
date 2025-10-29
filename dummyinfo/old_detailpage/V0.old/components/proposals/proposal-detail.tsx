import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"

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
  // Sample data based on the PDF example
  const proposalData = {
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
      {
        id: "99",
        name: "Verschil",
        inventoryCurrent: [0, 0, 0, 0, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 0, 0, 0, 0, 0, 0],
        sold: 0,
      },
    ],
  }

  // Calculate totals for each size
  const totals = proposalData.sizes.map((_, sizeIndex) => {
    return proposalData.stores.reduce((acc, store) => acc + store.inventoryCurrent[sizeIndex], 0)
  })

  const totalSold = proposalData.stores.reduce((acc, store) => acc + store.sold, 0)

  // Calculate totals for proposed
  const totalsProposed = proposalData.sizes.map((_, sizeIndex) => {
    return proposalData.stores.reduce((acc, store) => acc + store.inventoryProposed[sizeIndex], 0)
  })

  // Find differences between current and proposed
  const hasDifferences = proposalData.stores.some((store, storeIndex) => {
    return store.inventoryCurrent.some((current, sizeIndex) => {
      return current !== store.inventoryProposed[sizeIndex]
    })
  })

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
            <CardTitle>Interfiliaalverdeling</CardTitle>
            {hasDifferences && <Badge className="ml-2">Wijzigingen voorgesteld</Badge>}
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="comparison">
            <TabsList className="mb-4">
              <TabsTrigger value="comparison">Vergelijking</TabsTrigger>
              <TabsTrigger value="current">Huidige Situatie</TabsTrigger>
              <TabsTrigger value="proposed">Voorgestelde Situatie</TabsTrigger>
            </TabsList>

            <TabsContent value="comparison">
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
                      {totals.map((total, i) => (
                        <TableCell key={i} className="text-center">
                          {total}
                        </TableCell>
                      ))}
                      <TableCell className="text-center">{totalSold}</TableCell>
                    </TableRow>
                    {proposalData.stores.map((store) => {
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
                          {store.inventoryCurrent.map((qty, i) => {
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
                      {proposalData.sizes.map((size) => (
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
                      {totals.map((total, i) => (
                        <TableCell key={i} className="text-center">
                          {total}
                        </TableCell>
                      ))}
                      <TableCell className="text-center">{totalSold}</TableCell>
                    </TableRow>
                    {proposalData.stores.map((store) => {
                      // Skip rows with all zeros
                      const hasInventory = store.inventoryCurrent.some((val) => val > 0) || store.sold > 0
                      if (!hasInventory && store.id !== "0") return null

                      return (
                        <TableRow key={store.id}>
                          <TableCell>
                            {store.id} {store.name}
                          </TableCell>
                          {store.inventoryCurrent.map((qty, i) => (
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
                      {proposalData.sizes.map((size) => (
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
                      {totalsProposed.map((total, i) => (
                        <TableCell key={i} className="text-center">
                          {total}
                        </TableCell>
                      ))}
                      <TableCell className="text-center">{totalSold}</TableCell>
                    </TableRow>
                    {proposalData.stores.map((store) => {
                      // Skip rows with all zeros
                      const hasInventory = store.inventoryProposed.some((val) => val > 0) || store.sold > 0
                      if (!hasInventory && store.id !== "0") return null

                      return (
                        <TableRow key={store.id}>
                          <TableCell>
                            {store.id} {store.name}
                          </TableCell>
                          {store.inventoryProposed.map((qty, i) => {
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
