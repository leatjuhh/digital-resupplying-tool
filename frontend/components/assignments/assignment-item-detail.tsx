"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Check, X } from "lucide-react"
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

interface AssignmentItemDetailProps {
  id: string
  assignmentId: string
}

export function AssignmentItemDetail({ id, assignmentId }: AssignmentItemDetailProps) {
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false)
  const [failDialogOpen, setFailDialogOpen] = useState(false)
  const [failReason, setFailReason] = useState("")
  const [failSize, setFailSize] = useState("")
  const { toast } = useToast()

  const handleComplete = () => {
    toast({
      title: "Opdracht voltooid",
      description: `Opdracht voor artikel ${assignment.article} is gemarkeerd als voltooid.`,
    })
    setCompleteDialogOpen(false)
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
      description: `Opdracht voor artikel ${assignment.article} (maat ${failSize}) is gemarkeerd als niet uitgevoerd.`,
    })
    setFailDialogOpen(false)
    setFailReason("")
    setFailSize("")
  }

  // Sample data for the assignment
  const assignment = {
    id: assignmentId,
    article: "TC039-04",
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
    fromStore: "Etten-Leur",
    toStore: "Panningen",
    status: "Open",
    sizes: ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"],
    // Alleen de voorraad van de eigen winkel en de doelwinkel tonen
    stores: [
      {
        id: "35",
        name: "Etten-Leur",
        inventoryCurrent: [0, 0, 1, 2, 1, 1, 0, 0],
        inventoryProposed: [0, 0, 1, 1, 1, 1, 0, 0],
        sold: 2,
      },
      {
        id: "5",
        name: "Panningen",
        inventoryCurrent: [0, 0, 1, 1, 0, 0, 0, 0],
        inventoryProposed: [0, 0, 1, 2, 0, 0, 0, 0],
        sold: 6,
      },
    ],
  }

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-xl">Artikel Informatie</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Artikel</h3>
              <p className="font-medium">{assignment.description}</p>
              <p className="text-sm">Code: {assignment.article}</p>
              <p className="text-sm">Bestelcode: {assignment.orderCode}</p>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Collectie</h3>
              <p className="font-medium">{assignment.collection.name}</p>
              <p className="text-sm">Seizoen: {assignment.seasonYear}</p>
              <p className="text-sm">Collectiecode: {assignment.collection.id}</p>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-muted-foreground">Details</h3>
              <div className="flex items-center gap-2">
                <p className="font-medium">Kleur: {assignment.color.name}</p>
                <div
                  className="h-4 w-4 rounded-full border"
                  style={{ backgroundColor: assignment.color.name === "pink" ? "#f9a8d4" : "#cccccc" }}
                />
              </div>
              <p className="text-sm">
                Leverancier: {assignment.supplier.name} ({assignment.supplier.id})
              </p>
              <p className="text-sm">Categorie: {assignment.category.name}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Herverdelingsopdracht</CardTitle>
            <Badge variant={assignment.status === "Open" ? "outline" : "default"}>{assignment.status}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[120px] font-bold">Filiaal</TableHead>
                  {assignment.sizes.map((size, i) => (
                    <TableHead key={size} className="text-center min-w-[50px]">
                      {size}
                    </TableHead>
                  ))}
                  <TableHead className="text-center font-bold">Verkocht</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assignment.stores.map((store) => {
                  return (
                    <TableRow key={store.id}>
                      <TableCell>
                        {store.id} {store.name}
                        {store.name === assignment.fromStore && (
                          <Badge variant="outline" className="ml-2">
                            Van
                          </Badge>
                        )}
                        {store.name === assignment.toStore && (
                          <Badge variant="outline" className="ml-2">
                            Naar
                          </Badge>
                        )}
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
                <span>Voorgestelde voorraad (na herverdeling)</span>
              </div>
            </div>
          </div>

          {assignment.status === "Open" && (
            <div className="mt-6 flex justify-end gap-2">
              <Dialog open={completeDialogOpen} onOpenChange={setCompleteDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-green-600 hover:bg-green-700">
                    <Check className="mr-2 h-4 w-4" />
                    Markeer als voltooid
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Opdracht voltooien</DialogTitle>
                    <DialogDescription>
                      Bevestig dat u de herverdeling van artikel {assignment.article} ({assignment.description}) heeft
                      uitgevoerd.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="py-4">
                    <p>
                      U bevestigt dat u de volgende maten heeft overgebracht van {assignment.fromStore} naar{" "}
                      {assignment.toStore}:
                    </p>
                    <p className="font-medium mt-2">
                      {assignment.sizes.map((size, index) => {
                        const fromStore = assignment.stores.find((s) => s.name === assignment.fromStore)
                        const toStore = assignment.stores.find((s) => s.name === assignment.toStore)

                        if (!fromStore || !toStore) return null

                        const currentFrom = fromStore.inventoryCurrent[index]
                        const proposedFrom = fromStore.inventoryProposed[index]
                        const currentTo = toStore.inventoryCurrent[index]
                        const proposedTo = toStore.inventoryProposed[index]

                        const diff = proposedTo - currentTo

                        if (diff > 0) {
                          return (
                            <span key={size} className="mr-4">
                              {size}: {diff} stuks
                            </span>
                          )
                        }

                        return null
                      })}
                    </p>
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

              <Dialog open={failDialogOpen} onOpenChange={setFailDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="text-red-500">
                    <X className="mr-2 h-4 w-4" />
                    Kan niet uitvoeren
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Opdracht niet uitgevoerd</DialogTitle>
                    <DialogDescription>
                      Geef aan waarom de herverdeling van artikel {assignment.article} ({assignment.description}) niet
                      kon worden uitgevoerd.
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
                          {assignment.sizes.map((size) => {
                            const fromStore = assignment.stores.find((s) => s.name === assignment.fromStore)
                            const toStore = assignment.stores.find((s) => s.name === assignment.toStore)

                            if (!fromStore || !toStore) return null

                            const index = assignment.sizes.indexOf(size)
                            const currentFrom = fromStore.inventoryCurrent[index]
                            const proposedFrom = fromStore.inventoryProposed[index]
                            const currentTo = toStore.inventoryCurrent[index]
                            const proposedTo = toStore.inventoryProposed[index]

                            const diff = proposedTo - currentTo

                            if (diff > 0) {
                              return (
                                <SelectItem key={size} value={size}>
                                  {size}
                                </SelectItem>
                              )
                            }

                            return null
                          })}
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
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
