"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ShieldAlert } from "lucide-react";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { SettingsApi } from "@/components/settings/settings-api";
import { SettingsGeneral } from "@/components/settings/settings-general";
import { SettingsRoles } from "@/components/settings/settings-roles";
import { SettingsUsers } from "@/components/settings/settings-users";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { FeatureStatusBanner } from "@/components/ui/feature-status-banner";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/contexts/auth-context";

export function SettingsPageClient() {
  const router = useRouter();
  const { isAuthenticated, isLoading, hasPermission } = useAuth();

  const canViewSettings = hasPermission("view_settings");
  const canManageGeneral = hasPermission("manage_general_settings");
  const canManageUsers = hasPermission("manage_users");
  const canManageApi = hasPermission("manage_api_settings");
  const canManageRoles = hasPermission("manage_roles");

  useEffect(() => {
    if (isLoading) {
      return;
    }

    if (!isAuthenticated) {
      router.replace("/login?returnUrl=%2Fsettings");
      return;
    }

    if (!canViewSettings) {
      router.replace("/");
    }
  }, [canViewSettings, isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <DashboardShell>
        <DashboardHeader
          heading="Instellingen"
          text="Beheer applicatie instellingen en voorkeuren"
        />
        <div className="space-y-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-10 w-80" />
          <Skeleton className="h-[420px] w-full" />
        </div>
      </DashboardShell>
    );
  }

  if (!isAuthenticated || !canViewSettings) {
    return (
      <DashboardShell>
        <DashboardHeader
          heading="Instellingen"
          text="Beheer applicatie instellingen en voorkeuren"
        />
        <Alert>
          <ShieldAlert className="h-4 w-4" />
          <AlertTitle>Geen toegang tot instellingen</AlertTitle>
          <AlertDescription>
            Je wordt doorgestuurd omdat je account geen permissie heeft om deze pagina te openen.
          </AlertDescription>
        </Alert>
      </DashboardShell>
    );
  }

  const tabs = [
    {
      value: "general",
      label: "Algemeen",
      content: <SettingsGeneral canManage={canManageGeneral} />,
    },
    ...(canManageUsers
      ? [
          {
            value: "users",
            label: "Gebruikers",
            content: <SettingsUsers />,
          },
        ]
      : []),
    ...(canManageRoles
      ? [
          {
            value: "roles",
            label: "Rollen",
            content: <SettingsRoles />,
          },
        ]
      : []),
    ...(canManageApi
      ? [
          {
            value: "api",
            label: "API",
            content: <SettingsApi />,
          },
        ]
      : []),
  ];

  return (
    <DashboardShell>
      <DashboardHeader
        heading="Instellingen"
        text="Beheer applicatie instellingen, gebruikers, rollen en veilige integraties."
      />
      <FeatureStatusBanner description="Deze pagina gebruikt nu echte backenddata. Tabzichtbaarheid volgt permissies, wijzigingen gaan direct naar de API en de OpenAI key blijft write-only." />
      <Tabs defaultValue={tabs[0].value} className="mt-6">
        <TabsList className="flex h-auto flex-wrap justify-start gap-2 bg-transparent p-0">
          {tabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {tabs.map((tab) => (
          <TabsContent key={tab.value} value={tab.value} className="mt-6">
            {tab.content}
          </TabsContent>
        ))}
      </Tabs>
    </DashboardShell>
  );
}
