import { Clock3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

type PeriodSelectorProps = {
  note?: string | null;
};

export function PeriodSelector({ note }: PeriodSelectorProps) {
  return (
    <div className="flex max-w-md items-start gap-3 rounded-lg border bg-background px-4 py-3">
      <Clock3 className="mt-0.5 h-4 w-4 text-muted-foreground" />
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">Live totaal</Badge>
        </div>
        <p className="text-xs text-muted-foreground">
          {note || "Periodevergelijkingen zijn nog niet beschikbaar op echte backendsemantiek."}
        </p>
      </div>
    </div>
  );
}
