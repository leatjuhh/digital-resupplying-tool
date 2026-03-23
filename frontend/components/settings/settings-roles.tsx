"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { api, ManagedRole, RolePermission } from "@/lib/api";

function groupPermissions(permissions: RolePermission[]) {
  return permissions.reduce<Record<string, RolePermission[]>>((groups, permission) => {
    const key = permission.category || "overig";
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(permission);
    return groups;
  }, {});
}

export function SettingsRoles() {
  const { toast } = useToast();
  const [roles, setRoles] = useState<ManagedRole[]>([]);
  const [allPermissions, setAllPermissions] = useState<RolePermission[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [selectedPermissionIds, setSelectedPermissionIds] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let active = true;

    const loadData = async () => {
      try {
        const [rolesResponse, permissionsResponse] = await Promise.all([
          api.roles.list(),
          api.roles.getAllPermissions(),
        ]);

        if (!active) {
          return;
        }

        setRoles(rolesResponse);
        setAllPermissions(permissionsResponse);

        const initialRole = rolesResponse[0] ?? null;
        setSelectedRoleId(initialRole?.id ?? null);
        setSelectedPermissionIds(initialRole?.permissions.map((permission) => permission.id) ?? []);
      } catch (error) {
        if (!active) {
          return;
        }

        toast({
          title: "Rollen laden mislukt",
          description:
            error instanceof Error ? error.message : "Rollen of permissies konden niet worden geladen.",
          variant: "destructive",
        });
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    loadData();

    return () => {
      active = false;
    };
  }, [toast]);

  const selectedRole = roles.find((role) => role.id === selectedRoleId) ?? null;
  const permissionsByCategory = groupPermissions(allPermissions);

  const selectRole = (role: ManagedRole) => {
    setSelectedRoleId(role.id);
    setSelectedPermissionIds(role.permissions.map((permission) => permission.id));
  };

  const togglePermission = (permissionId: number, checked: boolean) => {
    setSelectedPermissionIds((current) => {
      if (checked) {
        return current.includes(permissionId) ? current : [...current, permissionId];
      }

      return current.filter((id) => id !== permissionId);
    });
  };

  const handleSave = async () => {
    if (!selectedRole) {
      return;
    }

    setIsSaving(true);
    try {
      await api.roles.updatePermissions(selectedRole.id, selectedPermissionIds);
      const refreshedRoles = await api.roles.list();
      setRoles(refreshedRoles);

      const refreshedRole = refreshedRoles.find((role) => role.id === selectedRole.id) ?? null;
      if (refreshedRole) {
        setSelectedRoleId(refreshedRole.id);
        setSelectedPermissionIds(refreshedRole.permissions.map((permission) => permission.id));
      }

      toast({
        title: "Rol bijgewerkt",
        description: `Permissies voor ${selectedRole.display_name} zijn opgeslagen.`,
      });
    } catch (error) {
      toast({
        title: "Opslaan mislukt",
        description:
          error instanceof Error ? error.message : "De permissiewijzigingen konden niet worden opgeslagen.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <Skeleton className="h-[420px] w-full" />
        <Skeleton className="h-[420px] w-full" />
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Rollen</CardTitle>
          <CardDescription>Selecteer een rol om permissies te beheren.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {roles.map((role) => (
            <button
              key={role.id}
              type="button"
              onClick={() => selectRole(role)}
              className={`w-full rounded-lg border p-3 text-left transition-colors ${
                selectedRoleId === role.id ? "border-primary bg-primary/5" : "hover:bg-muted/50"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium">{role.display_name}</span>
                {role.is_system_role && <Badge variant="outline">Systeem</Badge>}
              </div>
              <p className="mt-1 text-sm text-muted-foreground">{role.user_count} gebruiker(s)</p>
            </button>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{selectedRole?.display_name ?? "Rol"}</CardTitle>
          <CardDescription>
            {selectedRole?.description || "Werk permissies per categorie bij."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {selectedRole &&
            Object.entries(permissionsByCategory).map(([category, permissions]) => (
              <div key={category} className="space-y-4">
                <div>
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                    {category}
                  </h3>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  {permissions.map((permission) => (
                    <label
                      key={permission.id}
                      className="flex items-start gap-3 rounded-lg border p-3 transition-colors hover:bg-muted/40"
                    >
                      <Checkbox
                        checked={selectedPermissionIds.includes(permission.id)}
                        onCheckedChange={(checked) => togglePermission(permission.id, checked === true)}
                        disabled={isSaving}
                      />
                      <div className="space-y-1">
                        <Label className="cursor-pointer">{permission.display_name}</Label>
                        <p className="text-sm text-muted-foreground">{permission.description || permission.name}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          <div className="flex justify-end">
            <Button onClick={handleSave} disabled={!selectedRole || isSaving}>
              {isSaving ? "Bezig met opslaan..." : "Permissies Opslaan"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
