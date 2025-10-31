"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog"
import { useToast } from "@/hooks/use-toast"
import { Pencil, Trash2, Plus } from "lucide-react"

interface User {
  id: number
  name: string
  email: string
  role: "admin" | "user" | "store"
  status: "active" | "inactive"
  lastLogin: string
}

export function SettingsUsers() {
  const { toast } = useToast()
  const [users, setUsers] = useState<User[]>([
    {
      id: 1,
      name: "Admin Gebruiker",
      email: "admin@example.com",
      role: "admin",
      status: "active",
      lastLogin: "2025-10-31"
    },
    {
      id: 2,
      name: "Test Gebruiker",
      email: "user@example.com",
      role: "user",
      status: "active",
      lastLogin: "2025-10-30"
    }
  ])
  
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    role: "user" as "admin" | "user" | "store",
    password: ""
  })

  const handleAddUser = async () => {
    try {
      // TODO: Implement API call to POST /api/users
      const user: User = {
        id: users.length + 1,
        name: newUser.name,
        email: newUser.email,
        role: newUser.role,
        status: "active",
        lastLogin: "-"
      }
      
      setUsers([...users, user])
      setIsAddDialogOpen(false)
      setNewUser({ name: "", email: "", role: "user", password: "" })
      
      toast({
        title: "Gebruiker toegevoegd",
        description: "De nieuwe gebruiker is succesvol aangemaakt.",
      })
    } catch (error) {
      toast({
        title: "Fout bij toevoegen",
        description: "Er is een fout opgetreden bij het toevoegen van de gebruiker.",
        variant: "destructive",
      })
    }
  }

  const handleEditUser = async () => {
    if (!editingUser) return
    
    try {
      // TODO: Implement API call to PUT /api/users/{id}
      setUsers(users.map(u => u.id === editingUser.id ? editingUser : u))
      setIsEditDialogOpen(false)
      setEditingUser(null)
      
      toast({
        title: "Gebruiker bijgewerkt",
        description: "De gebruiker is succesvol bijgewerkt.",
      })
    } catch (error) {
      toast({
        title: "Fout bij bijwerken",
        description: "Er is een fout opgetreden bij het bijwerken van de gebruiker.",
        variant: "destructive",
      })
    }
  }

  const handleDeleteUser = async (userId: number) => {
    try {
      // TODO: Implement API call to DELETE /api/users/{id}
      setUsers(users.filter(u => u.id !== userId))
      
      toast({
        title: "Gebruiker verwijderd",
        description: "De gebruiker is succesvol verwijderd.",
      })
    } catch (error) {
      toast({
        title: "Fout bij verwijderen",
        description: "Er is een fout opgetreden bij het verwijderen van de gebruiker.",
        variant: "destructive",
      })
    }
  }

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case "admin": return "default"
      case "user": return "secondary"
      case "store": return "outline"
      default: return "secondary"
    }
  }

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "admin": return "Administrator"
      case "user": return "Gebruiker"
      case "store": return "Winkel"
      default: return role
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Gebruikersbeheer</CardTitle>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nieuwe Gebruiker
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Nieuwe gebruiker toevoegen</DialogTitle>
              <DialogDescription>
                Voeg een nieuwe gebruiker toe aan het systeem.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="new-name">Naam</Label>
                <Input
                  id="new-name"
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                  placeholder="Volledige naam"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-email">E-mailadres</Label>
                <Input
                  id="new-email"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  placeholder="gebruiker@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-role">Rol</Label>
                <Select value={newUser.role} onValueChange={(value: "admin" | "user" | "store") => setNewUser({ ...newUser, role: value })}>
                  <SelectTrigger id="new-role">
                    <SelectValue placeholder="Selecteer rol" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Administrator</SelectItem>
                    <SelectItem value="user">Gebruiker</SelectItem>
                    <SelectItem value="store">Winkel</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-password">Wachtwoord</Label>
                <Input
                  id="new-password"
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  placeholder="••••••••"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Annuleren
              </Button>
              <Button onClick={handleAddUser}>Toevoegen</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Naam</TableHead>
              <TableHead>E-mail</TableHead>
              <TableHead>Rol</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Laatste login</TableHead>
              <TableHead className="text-right">Acties</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell className="font-medium">{user.name}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Badge variant={getRoleBadgeVariant(user.role)}>
                    {getRoleLabel(user.role)}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge variant={user.status === "active" ? "default" : "secondary"}>
                    {user.status === "active" ? "Actief" : "Inactief"}
                  </Badge>
                </TableCell>
                <TableCell>{user.lastLogin}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Dialog open={isEditDialogOpen && editingUser?.id === user.id} onOpenChange={(open) => {
                      setIsEditDialogOpen(open)
                      if (!open) setEditingUser(null)
                    }}>
                      <DialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingUser(user)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Gebruiker bewerken</DialogTitle>
                          <DialogDescription>
                            Pas de gebruikersgegevens aan.
                          </DialogDescription>
                        </DialogHeader>
                        {editingUser && (
                          <div className="space-y-4">
                            <div className="space-y-2">
                              <Label htmlFor="edit-name">Naam</Label>
                              <Input
                                id="edit-name"
                                value={editingUser.name}
                                onChange={(e) => setEditingUser({ ...editingUser, name: e.target.value })}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="edit-email">E-mailadres</Label>
                              <Input
                                id="edit-email"
                                type="email"
                                value={editingUser.email}
                                onChange={(e) => setEditingUser({ ...editingUser, email: e.target.value })}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="edit-role">Rol</Label>
                              <Select value={editingUser.role} onValueChange={(value: "admin" | "user" | "store") => setEditingUser({ ...editingUser, role: value })}>
                                <SelectTrigger id="edit-role">
                                  <SelectValue placeholder="Selecteer rol" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="admin">Administrator</SelectItem>
                                  <SelectItem value="user">Gebruiker</SelectItem>
                                  <SelectItem value="store">Winkel</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="edit-status">Status</Label>
                              <Select value={editingUser.status} onValueChange={(value: "active" | "inactive") => setEditingUser({ ...editingUser, status: value })}>
                                <SelectTrigger id="edit-status">
                                  <SelectValue placeholder="Selecteer status" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="active">Actief</SelectItem>
                                  <SelectItem value="inactive">Inactief</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                          </div>
                        )}
                        <DialogFooter>
                          <Button variant="outline" onClick={() => {
                            setIsEditDialogOpen(false)
                            setEditingUser(null)
                          }}>
                            Annuleren
                          </Button>
                          <Button onClick={handleEditUser}>Opslaan</Button>
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
                            Weet je zeker dat je {user.name} wilt verwijderen? Deze actie kan niet ongedaan worden gemaakt.
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
  )
}
