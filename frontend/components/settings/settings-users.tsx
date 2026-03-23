"use client";

import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";
import { api, ManagedUser, ManagedUserCreateInput, ManagedUserUpdateInput, UserRoleOption } from "@/lib/api";

type UserFormState = {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role_id: number | null;
  is_active: boolean;
  store_code: string;
  store_name: string;
};

const emptyFormState: UserFormState = {
  username: "",
  email: "",
  full_name: "",
  password: "",
  role_id: null,
  is_active: true,
  store_code: "",
  store_name: "",
};

function formatDate(value: string | null) {
  if (!value) {
    return "Nog niet";
  }

  return new Intl.DateTimeFormat("nl-NL", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function SettingsUsers() {
  const { toast } = useToast();
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [roleOptions, setRoleOptions] = useState<UserRoleOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<ManagedUser | null>(null);
  const [formState, setFormState] = useState<UserFormState>(emptyFormState);

  useEffect(() => {
    let active = true;

    const loadData = async () => {
      try {
        const [usersResponse, rolesResponse] = await Promise.all([
          api.users.list(),
          api.users.getRoleOptions(),
        ]);

        if (!active) {
          return;
        }

        setUsers(usersResponse);
        setRoleOptions(rolesResponse);
      } catch (error) {
        if (!active) {
          return;
        }

        toast({
          title: "Gebruikers laden mislukt",
          description:
            error instanceof Error ? error.message : "Gebruikers of rollen konden niet worden geladen.",
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

  const selectedRole = roleOptions.find((role) => role.id === formState.role_id) ?? null;
  const isStoreRole = selectedRole?.name === "store";

  const resetForm = () => {
    setFormState(emptyFormState);
    setEditingUser(null);
  };

  const openAddDialog = () => {
    setFormState({
      ...emptyFormState,
      role_id: roleOptions[0]?.id ?? null,
    });
    setIsAddDialogOpen(true);
  };

  const openEditDialog = (user: ManagedUser) => {
    setEditingUser(user);
    setFormState({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      password: "",
      role_id: user.role_id,
      is_active: user.is_active,
      store_code: user.store_code ?? "",
      store_name: user.store_name ?? "",
    });
    setIsEditDialogOpen(true);
  };

  const updateForm = <K extends keyof UserFormState>(key: K, value: UserFormState[K]) => {
    setFormState((current) => ({ ...current, [key]: value }));
  };

  const handleRoleChange = (roleId: string) => {
    const role = roleOptions.find((option) => option.id === Number(roleId));

    setFormState((current) => ({
      ...current,
      role_id: Number(roleId),
      store_code: role?.name === "store" ? current.store_code : "",
      store_name: role?.name === "store" ? current.store_name : "",
    }));
  };

  const validateForm = (requiresPassword: boolean) => {
    if (!formState.username.trim() || !formState.email.trim() || !formState.full_name.trim()) {
      return "Gebruikersnaam, naam en e-mailadres zijn verplicht.";
    }

    if (!formState.role_id) {
      return "Selecteer een rol.";
    }

    if (requiresPassword && !formState.password) {
      return "Een wachtwoord is verplicht voor nieuwe gebruikers.";
    }

    if (isStoreRole && (!formState.store_code.trim() || !formState.store_name.trim())) {
      return "Store-gebruikers vereisen zowel store_code als store_name.";
    }

    return null;
  };

  const buildCreatePayload = (): ManagedUserCreateInput => ({
    username: formState.username.trim(),
    email: formState.email.trim(),
    full_name: formState.full_name.trim(),
    password: formState.password,
    role_id: formState.role_id as number,
    is_active: formState.is_active,
    store_code: isStoreRole ? formState.store_code.trim() : null,
    store_name: isStoreRole ? formState.store_name.trim() : null,
  });

  const buildUpdatePayload = (): ManagedUserUpdateInput => ({
    username: formState.username.trim(),
    email: formState.email.trim(),
    full_name: formState.full_name.trim(),
    role_id: formState.role_id as number,
    is_active: formState.is_active,
    store_code: isStoreRole ? formState.store_code.trim() : null,
    store_name: isStoreRole ? formState.store_name.trim() : null,
  });

  const handleAddUser = async () => {
    const validationError = validateForm(true);
    if (validationError) {
      toast({
        title: "Formulier onvolledig",
        description: validationError,
        variant: "destructive",
      });
      return;
    }

    setIsSaving(true);
    try {
      const createdUser = await api.users.create(buildCreatePayload());
      setUsers((current) => [...current, createdUser].sort((left, right) => left.username.localeCompare(right.username)));
      setIsAddDialogOpen(false);
      resetForm();

      toast({
        title: "Gebruiker toegevoegd",
        description: "De nieuwe gebruiker is succesvol aangemaakt.",
      });
    } catch (error) {
      toast({
        title: "Fout bij toevoegen",
        description:
          error instanceof Error ? error.message : "Er is een fout opgetreden bij het toevoegen van de gebruiker.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleEditUser = async () => {
    if (!editingUser) {
      return;
    }

    const validationError = validateForm(false);
    if (validationError) {
      toast({
        title: "Formulier onvolledig",
        description: validationError,
        variant: "destructive",
      });
      return;
    }

    setIsSaving(true);
    try {
      const updatedUser = await api.users.update(editingUser.id, buildUpdatePayload());
      setUsers((current) =>
        current
          .map((user) => (user.id === updatedUser.id ? updatedUser : user))
          .sort((left, right) => left.username.localeCompare(right.username))
      );
      setIsEditDialogOpen(false);
      resetForm();

      toast({
        title: "Gebruiker bijgewerkt",
        description: "De gebruiker is succesvol bijgewerkt.",
      });
    } catch (error) {
      toast({
        title: "Fout bij bijwerken",
        description:
          error instanceof Error ? error.message : "Er is een fout opgetreden bij het bijwerken van de gebruiker.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    try {
      await api.users.delete(userId);
      setUsers((current) => current.filter((user) => user.id !== userId));

      toast({
        title: "Gebruiker verwijderd",
        description: "De gebruiker is succesvol verwijderd.",
      });
    } catch (error) {
      toast({
        title: "Fout bij verwijderen",
        description:
          error instanceof Error ? error.message : "Er is een fout opgetreden bij het verwijderen van de gebruiker.",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Gebruikersbeheer</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-10 w-40" />
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <CardTitle>Gebruikersbeheer</CardTitle>
        <Dialog
          open={isAddDialogOpen}
          onOpenChange={(open) => {
            setIsAddDialogOpen(open);
            if (!open) {
              resetForm();
            }
          }}
        >
          <DialogTrigger asChild>
            <Button onClick={openAddDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Nieuwe Gebruiker
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Nieuwe gebruiker toevoegen</DialogTitle>
              <DialogDescription>Voeg een nieuwe gebruiker toe aan het systeem.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="new-username">Gebruikersnaam</Label>
                <Input
                  id="new-username"
                  value={formState.username}
                  onChange={(event) => updateForm("username", event.target.value)}
                  placeholder="bijvoorbeeld janssen"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-name">Naam</Label>
                <Input
                  id="new-name"
                  value={formState.full_name}
                  onChange={(event) => updateForm("full_name", event.target.value)}
                  placeholder="Volledige naam"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-email">E-mailadres</Label>
                <Input
                  id="new-email"
                  type="email"
                  value={formState.email}
                  onChange={(event) => updateForm("email", event.target.value)}
                  placeholder="gebruiker@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-role">Rol</Label>
                <Select value={formState.role_id?.toString() ?? ""} onValueChange={handleRoleChange}>
                  <SelectTrigger id="new-role">
                    <SelectValue placeholder="Selecteer rol" />
                  </SelectTrigger>
                  <SelectContent>
                    {roleOptions.map((role) => (
                      <SelectItem key={role.id} value={role.id.toString()}>
                        {role.display_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {isStoreRole && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="new-store-code">Store code</Label>
                    <Input
                      id="new-store-code"
                      value={formState.store_code}
                      onChange={(event) => updateForm("store_code", event.target.value)}
                      placeholder="bijvoorbeeld 9"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new-store-name">Store naam</Label>
                    <Input
                      id="new-store-name"
                      value={formState.store_name}
                      onChange={(event) => updateForm("store_name", event.target.value)}
                      placeholder="bijvoorbeeld Stein"
                    />
                  </div>
                </>
              )}
              <div className="space-y-2">
                <Label htmlFor="new-password">Wachtwoord</Label>
                <Input
                  id="new-password"
                  type="password"
                  value={formState.password}
                  onChange={(event) => updateForm("password", event.target.value)}
                  placeholder="••••••••"
                />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="new-active"
                  checked={formState.is_active}
                  onCheckedChange={(checked) => updateForm("is_active", checked === true)}
                />
                <Label htmlFor="new-active">Account actief</Label>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setIsAddDialogOpen(false);
                  resetForm();
                }}
              >
                Annuleren
              </Button>
              <Button onClick={handleAddUser} disabled={isSaving}>
                {isSaving ? "Bezig..." : "Toevoegen"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Gebruiker</TableHead>
              <TableHead>Rol</TableHead>
              <TableHead>Store</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Laatste login</TableHead>
              <TableHead className="text-right">Acties</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <div className="font-medium">{user.full_name}</div>
                  <div className="text-sm text-muted-foreground">
                    {user.username} · {user.email}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant={user.role_name === "admin" ? "default" : "secondary"}>
                    {user.role_display_name}
                  </Badge>
                </TableCell>
                <TableCell>{user.store_name ? `${user.store_name} (${user.store_code})` : "-"}</TableCell>
                <TableCell>
                  <Badge variant={user.is_active ? "default" : "secondary"}>
                    {user.is_active ? "Actief" : "Inactief"}
                  </Badge>
                </TableCell>
                <TableCell>{formatDate(user.last_login)}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Dialog
                      open={isEditDialogOpen && editingUser?.id === user.id}
                      onOpenChange={(open) => {
                        setIsEditDialogOpen(open);
                        if (!open) {
                          resetForm();
                        }
                      }}
                    >
                      <DialogTrigger asChild>
                        <Button variant="ghost" size="sm" onClick={() => openEditDialog(user)}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="sm:max-w-lg">
                        <DialogHeader>
                          <DialogTitle>Gebruiker bewerken</DialogTitle>
                          <DialogDescription>Pas de gebruikersgegevens aan.</DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div className="space-y-2">
                            <Label htmlFor="edit-username">Gebruikersnaam</Label>
                            <Input
                              id="edit-username"
                              value={formState.username}
                              onChange={(event) => updateForm("username", event.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="edit-name">Naam</Label>
                            <Input
                              id="edit-name"
                              value={formState.full_name}
                              onChange={(event) => updateForm("full_name", event.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="edit-email">E-mailadres</Label>
                            <Input
                              id="edit-email"
                              type="email"
                              value={formState.email}
                              onChange={(event) => updateForm("email", event.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="edit-role">Rol</Label>
                            <Select value={formState.role_id?.toString() ?? ""} onValueChange={handleRoleChange}>
                              <SelectTrigger id="edit-role">
                                <SelectValue placeholder="Selecteer rol" />
                              </SelectTrigger>
                              <SelectContent>
                                {roleOptions.map((role) => (
                                  <SelectItem key={role.id} value={role.id.toString()}>
                                    {role.display_name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          {isStoreRole && (
                            <>
                              <div className="space-y-2">
                                <Label htmlFor="edit-store-code">Store code</Label>
                                <Input
                                  id="edit-store-code"
                                  value={formState.store_code}
                                  onChange={(event) => updateForm("store_code", event.target.value)}
                                />
                              </div>
                              <div className="space-y-2">
                                <Label htmlFor="edit-store-name">Store naam</Label>
                                <Input
                                  id="edit-store-name"
                                  value={formState.store_name}
                                  onChange={(event) => updateForm("store_name", event.target.value)}
                                />
                              </div>
                            </>
                          )}
                          <div className="flex items-center gap-2">
                            <Checkbox
                              id="edit-active"
                              checked={formState.is_active}
                              onCheckedChange={(checked) => updateForm("is_active", checked === true)}
                            />
                            <Label htmlFor="edit-active">Account actief</Label>
                          </div>
                        </div>
                        <DialogFooter>
                          <Button
                            variant="outline"
                            onClick={() => {
                              setIsEditDialogOpen(false);
                              resetForm();
                            }}
                          >
                            Annuleren
                          </Button>
                          <Button onClick={handleEditUser} disabled={isSaving}>
                            {isSaving ? "Bezig..." : "Opslaan"}
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>

                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Gebruiker verwijderen</AlertDialogTitle>
                          <AlertDialogDescription>
                            Weet je zeker dat je {user.full_name} wilt verwijderen? Deze actie kan niet ongedaan worden
                            gemaakt.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Annuleren</AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleDeleteUser(user.id)}>
                            Verwijderen
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
