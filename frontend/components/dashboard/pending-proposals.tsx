"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardPendingBatch } from "@/lib/api";

type PendingProposalsProps = {
  batches: DashboardPendingBatch[];
  isLoading?: boolean;
};

function formatDate(value: string | null) {
  if (!value) {
    return "Onbekende datum";
  }

  return new Intl.DateTimeFormat("nl-NL", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function PendingProposals({ batches, isLoading = false }: PendingProposalsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center">
          <div className="grid gap-1">
            <CardTitle>Wachtende Reeksen</CardTitle>
            <p className="text-sm text-muted-foreground">Reeksen met open proposals op echte backenddata.</p>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
              <Skeleton className="h-2 w-full" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center">
        <div className="grid gap-1">
          <CardTitle>Wachtende Reeksen</CardTitle>
          <p className="text-sm text-muted-foreground">Reeksen met open proposals die nog beoordeling vragen.</p>
        </div>
        <Button asChild variant="ghost" size="sm" className="ml-auto">
          <Link href="/proposals">Alle bekijken</Link>
        </Button>
      </CardHeader>
      <CardContent>
        {batches.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Er staan momenteel geen batches met wachtende proposals open.
          </p>
        ) : (
          <div className="space-y-4">
            {batches.map((batch) => {
              const progressPercentage =
                batch.total_proposals > 0
                  ? Math.round((batch.reviewed_proposals / batch.total_proposals) * 100)
                  : 0;

              return (
                <div key={batch.batch_id} className="flex flex-col space-y-2">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm font-medium leading-none">
                        <Link href={`/proposals/batch/${batch.batch_id}`} className="hover:underline">
                          {batch.batch_name}
                        </Link>
                      </p>
                      <div className="flex items-center pt-1 text-sm text-muted-foreground">
                        <span>{formatDate(batch.created_at)}</span>
                        <span className="px-1">·</span>
                        <span>{batch.pending_proposals} wachtend</span>
                        <span className="px-1">·</span>
                        <span>{batch.total_proposals} totaal</span>
                      </div>
                    </div>
                    {batch.next_proposal_id ? (
                      <Button asChild size="sm" variant="outline" className="h-8">
                        <Link href={`/proposals/${batch.next_proposal_id}`}>
                          <span className="mr-1">Beoordelen</span>
                          <ArrowRight className="h-4 w-4" />
                        </Link>
                      </Button>
                    ) : null}
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span>
                        {batch.reviewed_proposals} van {batch.total_proposals} beoordeeld
                      </span>
                      <span className="font-medium">{progressPercentage}%</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-secondary">
                      <div className="h-full rounded-full bg-blue-500" style={{ width: `${progressPercentage}%` }} />
                    </div>
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
