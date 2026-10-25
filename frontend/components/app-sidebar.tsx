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
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { ModeToggle } from "@/components/mode-toggle"
import { useAuth } from "@/contexts/auth-context"

export function AppSidebar() {
  const pathname = usePathname()
  const { user, logout, hasPermission, hasRole } = useAuth()

  const isStoreUser = hasRole('store')
  const canViewDashboard = hasPermission("view_dashboard")
  const canViewSettings = hasPermission("view_settings")

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
      <SidebarHeader className="px-2 py-3">
        {/* Expanded state */}
        <div className="flex items-center justify-between group-data-[collapsible=icon]:hidden">
          <Link
            href="https://mc-company.nl/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div className="bg-white dark:bg-white/95 p-1.5 rounded-lg shadow-sm shrink-0">
              <Image
                src="/mc-company-logo.png"
                alt="MC Company Logo"
                width={150}
                height={118}
                className="h-auto w-10 object-contain"
              />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-base leading-tight">DRT</span>
              <span className="text-[10px] text-muted-foreground leading-tight">Digital Resupplying Tool</span>
            </div>
          </Link>
          <SidebarTrigger />
        </div>
        {/* Collapsed state: only trigger, centered */}
        <div className="hidden group-data-[collapsible=icon]:flex justify-center py-1">
          <SidebarTrigger />
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarMenu>
          {canViewDashboard && (
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={pathname === "/"} tooltip="Dashboard">
                <Link href="/">
                  <LayoutDashboard className="h-4 w-4" />
                  <span>Dashboard</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}

          {!isStoreUser && (
            <>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={pathname === "/uploads"} tooltip="Genereren">
                  <Link href="/uploads">
                    <FileUp className="h-4 w-4" />
                    <span>Genereren</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={pathname.startsWith("/proposals")} tooltip="Herverdelingsvoorstellen">
                  <Link href="/proposals">
                    <BarChart3 className="h-4 w-4" />
                    <span>Herverdelingsvoorstellen</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </>
          )}

          {isStoreUser && (
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={pathname.startsWith("/assignments")} tooltip="Opdrachten">
                <Link href="/assignments">
                  <ClipboardList className="h-4 w-4" />
                  <span>Opdrachten</span>
                  <Badge variant="outline" className="ml-auto text-[9px] uppercase tracking-wide group-data-[collapsible=icon]:hidden">
                    Niet leidend
                  </Badge>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}

          {canViewSettings && (
            <SidebarMenuItem>
              <SidebarMenuButton asChild isActive={pathname === "/settings"} tooltip="Instellingen">
                <Link href="/settings">
                  <Settings className="h-4 w-4" />
                  <span>Instellingen</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}
        </SidebarMenu>
      </SidebarContent>

      <SidebarFooter className="p-2">
        {/* Expanded footer */}
        <div className="flex items-center justify-between group-data-[collapsible=icon]:hidden px-2 py-1">
          <div className="flex items-center gap-2 min-w-0">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <span className="text-xs font-medium">{getUserInitials()}</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name || 'User'}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email || ''}</p>
            </div>
          </div>
          <ModeToggle />
        </div>
        <Button
          variant="outline"
          size="sm"
          className="group-data-[collapsible=icon]:hidden mt-1"
          onClick={() => logout()}
        >
          <LogOut className="mr-2 h-4 w-4" />
          Uitloggen
        </Button>

        {/* Collapsed footer: avatar tooltip + logout icon */}
        <div className="hidden group-data-[collapsible=icon]:flex flex-col items-center gap-2 py-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center cursor-default">
                <span className="text-xs font-medium">{getUserInitials()}</span>
              </div>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p className="font-medium text-sm">{user?.full_name || 'User'}</p>
              <p className="text-xs text-muted-foreground">{user?.email || ''}</p>
            </TooltipContent>
          </Tooltip>
          <button
            onClick={() => logout()}
            title="Uitloggen"
            className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-foreground transition-colors"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  )
}
