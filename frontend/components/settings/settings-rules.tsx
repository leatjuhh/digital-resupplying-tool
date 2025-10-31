"use client"

import { useState } from "react"
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

export function SettingsRules() {
  const { toast } = useToast()
  const [minStock, setMinStock] = useState("2")
  const [maxStock, setMaxStock] = useState("10")
  const [minStores, setMinStores] = useState("3")
  const [salesPeriod, setSalesPeriod] = useState("30")
  const [isLoading, setIsLoading] = useState(false)
  const [validationError, setValidationError] = useState("")

  const validateRules = (): boolean => {
    const min = parseInt(minStock)
    const max = parseInt(maxStock)
    const stores = parseInt(minStores)
    const period = parseInt(salesPeriod)

    if (isNaN(min) || isNaN(max) || isNaN(stores) || isNaN(period)) {
      setValidationError("Alle velden moeten geldige getallen bevatten")
      return false
    }

    if (min < 0) {
      setValidationError("Minimum voorraad mag niet negatief zijn")
      return false
    }

    if (max < 1) {
      setValidationError("Maximum voorraad moet minimaal 1 zijn")
      return false
    }

    if (min >= max) {
      setValidationError("Minimum voorraad moet kleiner zijn dan maximum voorraad")
      return false
    }

    if (stores < 1) {
      setValidationError("Minimum aantal winkels moet minimaal 1 zijn")
      return false
    }

    if (period < 1 || period > 365) {
      setValidationError("Verkoopcijfers periode moet tussen 1 en 365 dagen zijn")
      return false
    }

    setValidationError("")
    return true
  }

  const handleSave = async () => {
    if (!validateRules()) {
      return
    }

    setIsLoading(true)
    try {
      // TODO: Implement API call to PUT /api/settings/rules
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
      
      toast({
        title: "Regels opgeslagen",
        description: "De herverdelingsregels zijn succesvol bijgewerkt.",
      })
    } catch (error) {
      toast({
        title: "Fout bij opslaan",
        description: "Er is een fout opgetreden bij het opslaan van de regels.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Herverdelingsregels</CardTitle>
        <CardDescription>
          Configureer de regels voor het automatisch genereren van herverdelingsvoorstellen
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {validationError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{validationError}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          <Label htmlFor="min-stock">Minimum voorraad per winkel</Label>
          <Input
            id="min-stock"
            type="number"
            min="0"
            value={minStock}
            onChange={(e) => setMinStock(e.target.value)}
          />
          <p className="text-sm text-muted-foreground">
            Het minimum aantal artikelen dat per winkel op voorraad moet zijn
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="max-stock">Maximum voorraad per winkel</Label>
          <Input
            id="max-stock"
            type="number"
            min="1"
            value={maxStock}
            onChange={(e) => setMaxStock(e.target.value)}
          />
          <p className="text-sm text-muted-foreground">
            Het maximum aantal artikelen dat per winkel op voorraad mag zijn
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="min-stores">Minimum aantal winkels per artikel</Label>
          <Input
            id="min-stores"
            type="number"
            min="1"
            value={minStores}
            onChange={(e) => setMinStores(e.target.value)}
          />
          <p className="text-sm text-muted-foreground">
            Het minimum aantal winkels waarin een artikel beschikbaar moet zijn
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="sales-period">Verkoopcijfers periode (dagen)</Label>
          <Input
            id="sales-period"
            type="number"
            min="1"
            max="365"
            value={salesPeriod}
            onChange={(e) => setSalesPeriod(e.target.value)}
          />
          <p className="text-sm text-muted-foreground">
            Aantal dagen waarvoor verkoopcijfers worden geanalyseerd (1-365)
          </p>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? "Bezig met opslaan..." : "Regels Opslaan"}
        </Button>
      </CardFooter>
    </Card>
  )
}
