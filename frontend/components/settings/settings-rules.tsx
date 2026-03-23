"use client";

import { useEffect, useState } from "react";
import { AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { api, RulesSettings } from "@/lib/api";

const defaultRules: RulesSettings = {
  min_stock_per_store: 2,
  max_stock_per_store: 10,
  min_stores_per_article: 3,
  sales_period_days: 30,
};

type SettingsRulesProps = {
  canManage: boolean;
};

export function SettingsRules({ canManage }: SettingsRulesProps) {
  const { toast } = useToast();
  const [rules, setRules] = useState<RulesSettings>(defaultRules);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [validationError, setValidationError] = useState("");

  useEffect(() => {
    let active = true;

    const loadRules = async () => {
      try {
        const response = await api.settings.getRules();
        if (!active) {
          return;
        }

        setRules({
          min_stock_per_store: Number(response.min_stock_per_store ?? defaultRules.min_stock_per_store),
          max_stock_per_store: Number(response.max_stock_per_store ?? defaultRules.max_stock_per_store),
          min_stores_per_article: Number(
            response.min_stores_per_article ?? defaultRules.min_stores_per_article
          ),
          sales_period_days: Number(response.sales_period_days ?? defaultRules.sales_period_days),
        });
      } catch (error) {
        if (!active) {
          return;
        }

        toast({
          title: "Regels laden mislukt",
          description:
            error instanceof Error ? error.message : "De herverdelingsregels konden niet worden geladen.",
          variant: "destructive",
        });
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    loadRules();

    return () => {
      active = false;
    };
  }, [toast]);

  const updateRule = <K extends keyof RulesSettings>(key: K, value: number) => {
    setRules((current) => ({ ...current, [key]: value }));
  };

  const validateRules = (): boolean => {
    const min = rules.min_stock_per_store;
    const max = rules.max_stock_per_store;
    const stores = rules.min_stores_per_article;
    const period = rules.sales_period_days;

    if ([min, max, stores, period].some((value) => Number.isNaN(value))) {
      setValidationError("Alle velden moeten geldige getallen bevatten");
      return false;
    }

    if (min < 0) {
      setValidationError("Minimum voorraad mag niet negatief zijn");
      return false;
    }

    if (max < 1) {
      setValidationError("Maximum voorraad moet minimaal 1 zijn");
      return false;
    }

    if (min >= max) {
      setValidationError("Minimum voorraad moet kleiner zijn dan maximum voorraad");
      return false;
    }

    if (stores < 1) {
      setValidationError("Minimum aantal winkels moet minimaal 1 zijn");
      return false;
    }

    if (period < 1 || period > 365) {
      setValidationError("Verkoopcijfers periode moet tussen 1 en 365 dagen zijn");
      return false;
    }

    setValidationError("");
    return true;
  };

  const handleSave = async () => {
    if (!canManage || !validateRules()) {
      return;
    }

    setIsSaving(true);
    try {
      await api.settings.updateRules(rules);
      toast({
        title: "Regels opgeslagen",
        description: "De herverdelingsregels zijn succesvol bijgewerkt.",
      });
    } catch (error) {
      toast({
        title: "Fout bij opslaan",
        description:
          error instanceof Error ? error.message : "Er is een fout opgetreden bij het opslaan van de regels.",
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
          <CardTitle>Herverdelingsregels</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Herverdelingsregels</CardTitle>
        <CardDescription>
          Configureer de regels voor het automatisch genereren van herverdelingsvoorstellen.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {!canManage && (
          <Alert>
            <AlertDescription>
              Je kunt de huidige regels bekijken, maar niet aanpassen zonder `manage_rules_settings`.
            </AlertDescription>
          </Alert>
        )}

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
            value={rules.min_stock_per_store}
            onChange={(event) => updateRule("min_stock_per_store", Number(event.target.value))}
            disabled={!canManage || isSaving}
          />
          <p className="text-sm text-muted-foreground">
            Het minimum aantal artikelen dat per winkel op voorraad moet zijn.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="max-stock">Maximum voorraad per winkel</Label>
          <Input
            id="max-stock"
            type="number"
            min="1"
            value={rules.max_stock_per_store}
            onChange={(event) => updateRule("max_stock_per_store", Number(event.target.value))}
            disabled={!canManage || isSaving}
          />
          <p className="text-sm text-muted-foreground">
            Het maximum aantal artikelen dat per winkel op voorraad mag zijn.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="min-stores">Minimum aantal winkels per artikel</Label>
          <Input
            id="min-stores"
            type="number"
            min="1"
            value={rules.min_stores_per_article}
            onChange={(event) => updateRule("min_stores_per_article", Number(event.target.value))}
            disabled={!canManage || isSaving}
          />
          <p className="text-sm text-muted-foreground">
            Het minimum aantal winkels waarin een artikel beschikbaar moet zijn.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="sales-period">Verkoopcijfers periode (dagen)</Label>
          <Input
            id="sales-period"
            type="number"
            min="1"
            max="365"
            value={rules.sales_period_days}
            onChange={(event) => updateRule("sales_period_days", Number(event.target.value))}
            disabled={!canManage || isSaving}
          />
          <p className="text-sm text-muted-foreground">
            Aantal dagen waarvoor verkoopcijfers worden geanalyseerd (1-365).
          </p>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleSave} disabled={!canManage || isSaving}>
          {isSaving ? "Bezig met opslaan..." : "Regels Opslaan"}
        </Button>
      </CardFooter>
    </Card>
  );
}
