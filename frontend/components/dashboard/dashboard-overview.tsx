"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle } from "lucide-react";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { DashboardStats } from "@/components/dashboard/dashboard-stats";
import { NotificationsList } from "@/components/dashboard/notifications-list";
import { PendingProposals } from "@/components/dashboard/pending-proposals";
import { PeriodSelector } from "@/components/dashboard/period-selector";
import { RecentActivity } from "@/components/dashboard/recent-activity";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useAuth } from "@/contexts/auth-context";
import { api, DashboardSummary } from "@/lib/api";

export function DashboardOverview() {
  const router = useRouter();
  const { hasPermission, isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const canViewDashboard = hasPermission("view_dashboard");
  const fallbackHref = hasPermission("view_proposals")
    ? "/proposals"
    : hasPermission("view_assignments")
      ? "/assignments"
      : hasPermission("view_settings")
        ? "/settings"
        : "/login";

  useEffect(() => {
    if (isAuthLoading) {
      return;
    }

    if (!isAuthenticated) {
      return;
    }

    if (!canViewDashboard) {
      router.replace(fallbackHref);
    }
  }, [canViewDashboard, fallbackHref, isAuthenticated, isAuthLoading, router]);

  useEffect(() => {
    if (isAuthLoading || !isAuthenticated || !canViewDashboard) {
      if (!isAuthLoading) {
        setIsLoading(false);
      }
      return;
    }

    let active = true;

    const loadSummary = async () => {
      try {
        setIsLoading(true);
        const response = await api.dashboard.getSummary();
        if (!active) {
          return;
        }

        setSummary(response);
        setError(null);
      } catch (loadError) {
        if (!active) {
          return;
        }

        setError(
          loadError instanceof Error
            ? loadError.message
            : "Het dashboardoverzicht kon niet worden geladen.",
        );
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    loadSummary();

    return () => {
      active = false;
    };
  }, [canViewDashboard, isAuthenticated, isAuthLoading]);

  if (isAuthLoading) {
    return (
      <DashboardShell>
        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <DashboardStats stats={null} isLoading />
        </div>
      </DashboardShell>
    );
  }

  return (
    <DashboardShell>
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <DashboardHeader
          heading="Dashboard"
          text="Live overzicht van proposals, batches en store-uitvoering op basis van echte backenddata."
        />
        <PeriodSelector note={summary?.period_note} />
      </div>

      {error && (
        <Alert variant="destructive" className="mt-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Dashboard laden mislukt</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {!isAuthenticated || !canViewDashboard ? (
        <Alert className="mt-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Geen toegang tot dashboard</AlertTitle>
          <AlertDescription>
            Je wordt doorgestuurd naar een route waarvoor je account wel rechten heeft.
          </AlertDescription>
        </Alert>
      ) : (
        <>
          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <DashboardStats stats={summary?.stats ?? null} isLoading={isLoading} />
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <PendingProposals batches={summary?.pending_batches ?? []} isLoading={isLoading} />
            </div>
            <div className="space-y-4">
              <RecentActivity events={summary?.recent_activity ?? []} isLoading={isLoading} />
              <NotificationsList items={summary?.attention_items ?? []} isLoading={isLoading} />
            </div>
          </div>
        </>
      )}
    </DashboardShell>
  );
}
