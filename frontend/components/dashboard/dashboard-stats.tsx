import { ClipboardList, FileCheck, FileClock, Store } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardStatsSummary } from "@/lib/api";

type DashboardStatsProps = {
  stats: DashboardStatsSummary | null;
  isLoading?: boolean;
};

type StatCard = {
  title: string;
  value: number;
  description: string;
  icon: typeof FileCheck;
};

export function DashboardStats({ stats, isLoading = false }: DashboardStatsProps) {
  if (isLoading || !stats) {
    return (
      <>
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-4 w-4 rounded-full" />
            </CardHeader>
            <CardContent className="space-y-2">
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-4 w-full" />
            </CardContent>
          </Card>
        ))}
      </>
    );
  }

  const cards: StatCard[] = [
    {
      title: "Totaal Voorstellen",
      value: stats.total_proposals,
      description: `${stats.approved_proposals} goedgekeurd, ${stats.rejected_proposals} afgekeurd, ${stats.edited_proposals} bewerkt`,
      icon: FileCheck,
    },
    {
      title: "Wachtend op Beoordeling",
      value: stats.pending_proposals,
      description: `${stats.total_batches} batch(es) ingelezen, ${stats.assignment_series_count} assignmentreeks(en) actief`,
      icon: FileClock,
    },
    {
      title: "Open Opdrachten",
      value: stats.open_assignment_items,
      description: `${stats.completed_assignment_items} voltooid, ${stats.failed_assignment_items} met aandacht`,
      icon: ClipboardList,
    },
    {
      title: "Actieve Winkels",
      value: stats.active_store_count,
      description: "Gebaseerd op winkels die in de ingelezen batchdata voorkomen",
      icon: Store,
    },
  ];

  return (
    <>
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
              <p className="mt-1 text-xs text-muted-foreground">{card.description}</p>
            </CardContent>
          </Card>
        );
      })}
    </>
  );
}
