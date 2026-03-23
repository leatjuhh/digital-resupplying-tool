import Link from "next/link";
import { AlertTriangle, CheckCircle2, ClipboardList, Files } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardEvent } from "@/lib/api";

type RecentActivityProps = {
  events: DashboardEvent[];
  isLoading?: boolean;
};

function formatTimestamp(value: string | null) {
  if (!value) {
    return "Onbekend tijdstip";
  }

  return new Intl.DateTimeFormat("nl-NL", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function getEventIcon(kind: DashboardEvent["kind"]) {
  switch (kind) {
    case "proposal":
      return CheckCircle2;
    case "assignment":
      return ClipboardList;
    case "parse_log":
      return AlertTriangle;
    default:
      return Files;
  }
}

export function RecentActivity({ events, isLoading = false }: RecentActivityProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recente Activiteit</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="flex items-start gap-4">
              <Skeleton className="h-8 w-8 rounded-full" />
              <div className="w-full space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-1/3" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recente Activiteit</CardTitle>
      </CardHeader>
      <CardContent>
        {events.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nog geen recente systeemevents beschikbaar.</p>
        ) : (
          <div className="space-y-4">
            {events.map((event) => {
              const Icon = getEventIcon(event.kind);

              return (
                <div key={event.id} className="flex items-start gap-4">
                  <div className="rounded-full bg-muted p-2">
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium leading-none">{event.title}</p>
                    {event.href ? (
                      <Link href={event.href} className="text-sm text-muted-foreground hover:underline">
                        {event.description}
                      </Link>
                    ) : (
                      <p className="text-sm text-muted-foreground">{event.description}</p>
                    )}
                    <p className="text-xs text-muted-foreground">{formatTimestamp(event.created_at)}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
