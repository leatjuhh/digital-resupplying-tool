"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { api, GeneralSettings } from "@/lib/api";

const defaultSettings: GeneralSettings = {
  app_name: "Digital Resupplying",
  language: "nl",
  timezone: "Europe/Amsterdam",
  email_notifications: true,
};

type SettingsGeneralProps = {
  canManage: boolean;
};

export function SettingsGeneral({ canManage }: SettingsGeneralProps) {
  const { toast } = useToast();
  const [settings, setSettings] = useState<GeneralSettings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let active = true;

    const loadSettings = async () => {
      try {
        const response = await api.settings.getGeneral();
        if (!active) {
          return;
        }

        setSettings({
          app_name: response.app_name ?? defaultSettings.app_name,
          language: response.language ?? defaultSettings.language,
          timezone: response.timezone ?? defaultSettings.timezone,
          email_notifications:
            typeof response.email_notifications === "boolean"
              ? response.email_notifications
              : defaultSettings.email_notifications,
        });
      } catch (error) {
        if (!active) {
          return;
        }

        toast({
          title: "Instellingen laden mislukt",
          description:
            error instanceof Error
              ? error.message
              : "De algemene instellingen konden niet worden geladen.",
          variant: "destructive",
        });
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    loadSettings();

    return () => {
      active = false;
    };
  }, [toast]);

  const updateSetting = <K extends keyof GeneralSettings>(key: K, value: GeneralSettings[K]) => {
    setSettings((current) => ({ ...current, [key]: value }));
  };

  const handleSave = async () => {
    if (!canManage) {
      return;
    }

    setIsSaving(true);
    try {
      await api.settings.updateGeneral(settings);
      toast({
        title: "Instellingen opgeslagen",
        description: "De algemene instellingen zijn succesvol bijgewerkt.",
      });
    } catch (error) {
      toast({
        title: "Fout bij opslaan",
        description:
          error instanceof Error
            ? error.message
            : "Er is een fout opgetreden bij het opslaan van de instellingen.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Applicatie Instellingen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-16 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Applicatie Instellingen</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {!canManage && (
          <Alert>
            <AlertDescription>
              Je hebt alleen leesrechten voor algemene instellingen. Wijzigingen opslaan is uitgeschakeld.
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          <Label htmlFor="app-name">Applicatie Naam</Label>
          <Input
            id="app-name"
            value={settings.app_name}
            onChange={(event) => updateSetting("app_name", event.target.value)}
            placeholder="Digital Resupplying"
            disabled={!canManage || isSaving}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="language">Taal</Label>
          <Select
            value={settings.language}
            onValueChange={(value) => updateSetting("language", value)}
            disabled={!canManage || isSaving}
          >
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
          <Select
            value={settings.timezone}
            onValueChange={(value) => updateSetting("timezone", value)}
            disabled={!canManage || isSaving}
          >
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
            checked={settings.email_notifications}
            onCheckedChange={(checked) => updateSetting("email_notifications", checked === true)}
            disabled={!canManage || isSaving}
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
        <Button onClick={handleSave} disabled={!canManage || isSaving}>
          {isSaving ? "Bezig met opslaan..." : "Instellingen Opslaan"}
        </Button>
      </CardFooter>
    </Card>
  );
}
