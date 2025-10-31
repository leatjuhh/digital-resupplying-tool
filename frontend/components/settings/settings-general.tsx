"use client"

import { useState } from "react"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"

export function SettingsGeneral() {
  const { toast } = useToast()
  const [appName, setAppName] = useState("Digital Resupplying")
  const [language, setLanguage] = useState("nl")
  const [timezone, setTimezone] = useState("Europe/Amsterdam")
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  const handleSave = async () => {
    setIsLoading(true)
    try {
      // TODO: Implement API call to PUT /api/settings
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
      
      toast({
        title: "Instellingen opgeslagen",
        description: "De algemene instellingen zijn succesvol bijgewerkt.",
      })
    } catch (error) {
      toast({
        title: "Fout bij opslaan",
        description: "Er is een fout opgetreden bij het opslaan van de instellingen.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Applicatie Instellingen</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="app-name">Applicatie Naam</Label>
          <Input 
            id="app-name" 
            value={appName}
            onChange={(e) => setAppName(e.target.value)}
            placeholder="Digital Resupplying"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="language">Taal</Label>
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger id="language">
              <SelectValue placeholder="Selecteer taal" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="nl">Nederlands</SelectItem>
              <SelectItem value="en">Engels</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="timezone">Tijdzone</Label>
          <Select value={timezone} onValueChange={setTimezone}>
            <SelectTrigger id="timezone">
              <SelectValue placeholder="Selecteer tijdzone" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Europe/Amsterdam">Europe/Amsterdam (GMT+1)</SelectItem>
              <SelectItem value="Europe/Brussels">Europe/Brussels (GMT+1)</SelectItem>
              <SelectItem value="Europe/London">Europe/London (GMT+0)</SelectItem>
              <SelectItem value="Europe/Paris">Europe/Paris (GMT+1)</SelectItem>
              <SelectItem value="America/New_York">America/New York (GMT-5)</SelectItem>
              <SelectItem value="America/Los_Angeles">America/Los Angeles (GMT-8)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox 
            id="email-notifications"
            checked={emailNotifications}
            onCheckedChange={(checked) => setEmailNotifications(checked as boolean)}
          />
          <div className="space-y-1">
            <Label 
              htmlFor="email-notifications"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              E-mail notificaties
            </Label>
            <p className="text-sm text-muted-foreground">
              Ontvang e-mail notificaties voor nieuwe voorstellen
            </p>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? "Bezig met opslaan..." : "Instellingen Opslaan"}
        </Button>
      </CardFooter>
    </Card>
  )
}
