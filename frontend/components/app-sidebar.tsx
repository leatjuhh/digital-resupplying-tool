"use client"

import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { BarChart3, FileUp, LayoutDashboard, LogOut, Settings, ClipboardList } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { ModeToggle } from "@/components/mode-toggle"
import { useAuth } from "@/contexts/auth-context"

export function AppSidebar() {
  const pathname = usePathname()
  const { user, logout, hasPermission, hasRole } = useAuth()

  // Check if user has store role
  const isStoreUser = hasRole('store')
  const canViewDashboard = hasPermission("view_dashboard")
  const canViewSettings = hasPermission("view_settings")

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user?.full_name) return 'U'
    return user.full_name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="flex items-center justify-between px-4 py-4">
        <Link 
          href="https://mc-company.nl/" 
          target="_blank" 
          rel="noopener noreferrer"
          className="flex items-center gap-3 hover:opacity-80 transition-opacity group"
        >
          <div className="bg-white dark:bg-white/95 p-2 rounded-lg shadow-sm">
            <Image 
              src="/mc-company-logo.png" 
              alt="MC Company Logo" 
              width={150}
              height={118}
              className="h-auto w-12 object-contain"
            />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg leading-tight">DRT</span>
            <span className="text-[10px] text-muted-foreground leading-tight">Digital Resupplying Tool</span>
          </div>
        </Link>
        <SidebarTrigger />
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          {canViewDashboard && (
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={pathname === "/"}>
                <Link href="/">
                  <LayoutDashboard className="mr-2 h-4 w-4" />
                  <span>Dashboard</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}

          {!isStoreUser && (
            <>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={pathname === "/uploads"}>
                  <Link href="/uploads">
                    <FileUp className="mr-2 h-4 w-4" />
                    <span>Genereren</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={pathname.startsWith("/proposals")}>
                  <Link href="/proposals">
                    <BarChart3 className="mr-2 h-4 w-4" />
                    <span>Herverdelingsvoorstellen</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </>
          )}

          {isStoreUser && (
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={pathname.startsWith("/assignments")}>
                <Link href="/assignments">
                  <ClipboardList className="mr-2 h-4 w-4" />
                  <span>Opdrachten</span>
                  <Badge variant="outline" className="ml-auto text-[9px] uppercase tracking-wide">
                    Niet leidend
                  </Badge>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}

          {canViewSettings && (
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={pathname === "/settings"}>
                <Link href="/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Instellingen</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter className="p-4 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-xs font-medium">{getUserInitials()}</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name || 'User'}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email || ''}</p>
            </div>
          </div>
          <ModeToggle />
        </div>
        <Button variant="outline" size="sm" className="mt-2" onClick={() => logout()}>
          <LogOut className="mr-2 h-4 w-4" />
          Uitloggen
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}
