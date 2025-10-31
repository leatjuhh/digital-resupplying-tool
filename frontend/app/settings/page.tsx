import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SettingsGeneral } from "@/components/settings/settings-general"
import { SettingsUsers } from "@/components/settings/settings-users"
import { SettingsRules } from "@/components/settings/settings-rules"
import { SettingsApi } from "@/components/settings/settings-api"

export default function SettingsPage() {
  // TODO: Get user role from auth context
  const userRole = "admin" // Placeholder
  
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Instellingen"
        text="Beheer applicatie instellingen en voorkeuren"
      />
      <Tabs defaultValue="general" className="mt-6">
        <TabsList>
          <TabsTrigger value="general">Algemeen</TabsTrigger>
          {userRole === "admin" && (
            <TabsTrigger value="users">Gebruikers</TabsTrigger>
          )}
          {["admin", "user"].includes(userRole) && (
            <TabsTrigger value="rules">Regels</TabsTrigger>
          )}
          {userRole === "admin" && (
            <TabsTrigger value="api">API</TabsTrigger>
          )}
        </TabsList>
        
        <TabsContent value="general">
          <SettingsGeneral />
        </TabsContent>
        
        {userRole === "admin" && (
          <TabsContent value="users">
            <SettingsUsers />
          </TabsContent>
        )}
        
        {["admin", "user"].includes(userRole) && (
          <TabsContent value="rules">
            <SettingsRules />
          </TabsContent>
        )}
        
        {userRole === "admin" && (
          <TabsContent value="api">
            <SettingsApi />
          </TabsContent>
        )}
      </Tabs>
    </DashboardShell>
  )
}
