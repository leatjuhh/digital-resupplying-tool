"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, FileUp, LayoutDashboard, LogOut, Settings, ShoppingBag, ClipboardList } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { ModeToggle } from "@/components/mode-toggle"

export function AppSidebar() {
  const pathname = usePathname()

  // Simuleer een winkelgebruiker (in een echte app zou dit uit de authenticatie komen)
  const isStoreUser = false

  return (
    <Sidebar>
      <SidebarHeader className="flex items-center justify-between px-4 py-2">
        <Link href="/" className="flex items-center gap-2">
          <ShoppingBag className="h-6 w-6" />
          <span className="font-bold">Digital Resupplying</span>
        </Link>
        <SidebarTrigger />
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild isActive={pathname === "/"}>
              <Link href="/">
                <LayoutDashboard className="mr-2 h-4 w-4" />
                <span>Dashboard</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>

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
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )}

          <SidebarMenuItem>
            <SidebarMenuButton asChild isActive={pathname === "/settings"}>
              <Link href="/settings">
                <Settings className="mr-2 h-4 w-4" />
                <span>Instellingen</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter className="p-4 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-xs font-medium">AB</span>
            </div>
            <div>
              <p className="text-sm font-medium">Admin Beheerder</p>
              <p className="text-xs text-muted-foreground">admin@example.com</p>
            </div>
          </div>
          <ModeToggle />
        </div>
        <Button variant="outline" size="sm" className="mt-2">
          <LogOut className="mr-2 h-4 w-4" />
          Uitloggen
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}
