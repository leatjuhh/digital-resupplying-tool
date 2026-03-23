"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, XCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { api, ApiKeyStatus } from "@/lib/api";

const defaultStatus: ApiKeyStatus = {
  configured: false,
  masked_key: null,
  updated_at: null,
};

export function SettingsApi() {
  const { toast } = useToast();
  const [apiKey, setApiKey] = useState("");
  const [storedStatus, setStoredStatus] = useState<ApiKeyStatus>(defaultStatus);
  const [isLoading, setIsLoading] = useState(true);
  const [isValidating, setIsValidating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [validationStatus, setValidationStatus] = useState<"idle" | "valid" | "invalid">("idle");
  const [validationMessage, setValidationMessage] = useState("");

  useEffect(() => {
    let active = true;

    const loadStatus = async () => {
      try {
        const response = await api.settings.getApiKeyStatus();
        if (active) {
          setStoredStatus(response);
        }
      } catch (error) {
        if (!active) {
          return;
        }

        toast({
          title: "API status laden mislukt",
          description:
            error instanceof Error ? error.message : "De status van de API key kon niet worden geladen.",
          variant: "destructive",
        });
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    loadStatus();

    return () => {
      active = false;
    };
  }, [toast]);

  const handleValidate = async () => {
    if (!apiKey || !apiKey.startsWith("sk-")) {
      toast({
        title: "Ongeldige API key",
        description: "De API key moet beginnen met 'sk-'",
        variant: "destructive",
      });
      return;
    }

    setIsValidating(true);
    try {
      const response = await api.settings.validateApiKey(apiKey);
      setValidationStatus(response.valid ? "valid" : "invalid");
      setValidationMessage(response.message);

      toast({
        title: response.valid ? "API key gevalideerd" : "API key ongeldig",
        description: response.message,
        variant: response.valid ? "default" : "destructive",
      });
    } catch (error) {
      setValidationStatus("invalid");
      setValidationMessage(
        error instanceof Error ? error.message : "Er is een fout opgetreden bij het valideren van de API key."
      );
      toast({
        title: "Validatie mislukt",
        description:
          error instanceof Error ? error.message : "Er is een fout opgetreden bij het valideren van de API key.",
        variant: "destructive",
      });
    } finally {
      setIsValidating(false);
    }
  };

  const handleSave = async () => {
    if (!apiKey) {
      toast({
        title: "Geen API key",
        description: "Voer een API key in voordat je opslaat.",
        variant: "destructive",
      });
      return;
    }

    setIsSaving(true);
    try {
      const response = await api.settings.updateOpenAiKey(apiKey);
      setStoredStatus({
        configured: true,
        masked_key: response.masked_key,
        updated_at: new Date().toISOString(),
      });
      setApiKey("");
      setValidationStatus("idle");
      setValidationMessage("");

      toast({
        title: "API instellingen opgeslagen",
        description: response.message,
      });
    } catch (error) {
      toast({
        title: "Fout bij opslaan",
        description:
          error instanceof Error ? error.message : "Er is een fout opgetreden bij het opslaan van de API instellingen.",
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
          <CardTitle>API Instellingen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-56" />
          <Skeleton className="h-16 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Instellingen</CardTitle>
        <CardDescription>
          Configureer veilige integraties. De opgeslagen OpenAI key wordt nooit onversleuteld teruggestuurd naar de frontend.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="rounded-lg border bg-muted/30 p-4 text-sm">
          <div className="font-medium">Huidige status</div>
          <p className="mt-1 text-muted-foreground">
            {storedStatus.configured
              ? `Geconfigureerd als ${storedStatus.masked_key ?? "verborgen"}`
              : "Nog geen OpenAI API key opgeslagen."}
          </p>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="openai-key">Nieuwe OpenAI API Key</Label>
            <Input
              id="openai-key"
              type="password"
              value={apiKey}
              onChange={(event) => {
                setApiKey(event.target.value);
                setValidationStatus("idle");
                setValidationMessage("");
              }}
              placeholder="sk-..."
              disabled={isSaving}
            />
            <p className="text-sm text-muted-foreground">
              Vereist voor AI-suggesties en analysefunctionaliteiten.
            </p>
          </div>

          <Button variant="outline" onClick={handleValidate} disabled={isValidating || isSaving || !apiKey}>
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
                {validationMessage ||
                  (validationStatus === "valid"
                    ? "API key is geldig en kan worden gebruikt."
                    : "API key is ongeldig of heeft geen toegang.")}
              </AlertDescription>
            </Alert>
          )}
        </div>

        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Bewaar API keys veilig. De backend bewaart alleen masked metadata voor readback naar de UI.
          </AlertDescription>
        </Alert>
      </CardContent>
      <CardFooter>
        <Button onClick={handleSave} disabled={isSaving || !apiKey}>
          {isSaving ? "Bezig met opslaan..." : "API Instellingen Opslaan"}
        </Button>
      </CardFooter>
    </Card>
  );
}
