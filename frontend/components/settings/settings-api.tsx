"use client"

import { useState } from "react"
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react"

export function SettingsApi() {
  const { toast } = useToast()
  const [apiKey, setApiKey] = useState("")
  const [isValidating, setIsValidating] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [validationStatus, setValidationStatus] = useState<"idle" | "valid" | "invalid">("idle")

  const handleValidate = async () => {
    if (!apiKey || !apiKey.startsWith("sk-")) {
      toast({
        title: "Ongeldige API key",
        description: "De API key moet beginnen met 'sk-'",
        variant: "destructive",
      })
      return
    }

    setIsValidating(true)
    try {
      // TODO: Implement API call to POST /api/settings/validate-api-key
      await new Promise(resolve => setTimeout(resolve, 1500)) // Simulate API call
      
      // Simulate validation result
      const isValid = apiKey.length > 20 // Simple mock validation
      
      if (isValid) {
        setValidationStatus("valid")
        toast({
          title: "API key gevalideerd",
          description: "De OpenAI API key is geldig.",
        })
      } else {
        setValidationStatus("invalid")
        toast({
          title: "Ongeldige API key",
          description: "De OpenAI API key is ongeldig of heeft geen toegang.",
          variant: "destructive",
        })
      }
    } catch (error) {
      setValidationStatus("invalid")
      toast({
        title: "Validatie mislukt",
        description: "Er is een fout opgetreden bij het valideren van de API key.",
        variant: "destructive",
      })
    } finally {
      setIsValidating(false)
    }
  }

  const handleSave = async () => {
    if (!apiKey) {
      toast({
        title: "Geen API key",
        description: "Voer een API key in voordat u opslaat.",
        variant: "destructive",
      })
      return
    }

    setIsSaving(true)
    try {
      // TODO: Implement API call to PUT /api/settings/api
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
      
      toast({
        title: "API instellingen opgeslagen",
        description: "De API instellingen zijn succesvol bijgewerkt.",
      })
    } catch (error) {
      toast({
        title: "Fout bij opslaan",
        description: "Er is een fout opgetreden bij het opslaan van de API instellingen.",
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Instellingen</CardTitle>
        <CardDescription>
          Configureer externe API verbindingen voor geavanceerde functies
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="openai-key">OpenAI API Key</Label>
            <Input
              id="openai-key"
              type="password"
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value)
                setValidationStatus("idle")
              }}
              placeholder="sk-..."
            />
            <p className="text-sm text-muted-foreground">
              Vereist voor AI-suggesties en analyse functionaliteiten
            </p>
          </div>

          <Button 
            variant="outline" 
            onClick={handleValidate}
            disabled={isValidating || !apiKey}
          >
            {isValidating ? "Bezig met valideren..." : "Valideer API Key"}
          </Button>

          {validationStatus !== "idle" && (
            <Alert variant={validationStatus === "valid" ? "default" : "destructive"}>
              {validationStatus === "valid" ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                <XCircle className="h-4 w-4" />
              )}
              <AlertDescription>
                {validationStatus === "valid" 
                  ? "API key is geldig en kan worden gebruikt" 
                  : "API key is ongeldig of heeft geen toegang"}
              </AlertDescription>
            </Alert>
          )}
        </div>

        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Belangrijk:</strong> Bewaar uw API keys veilig en deel ze nooit met anderen. 
            De API key wordt versleuteld opgeslagen in de database.
          </AlertDescription>
        </Alert>
      </CardContent>
      <CardFooter>
        <Button onClick={handleSave} disabled={isSaving || !apiKey}>
          {isSaving ? "Bezig met opslaan..." : "API Instellingen Opslaan"}
        </Button>
      </CardFooter>
    </Card>
  )
}
