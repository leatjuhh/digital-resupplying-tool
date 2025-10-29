"use client"

import Link from "next/link"
import { useState } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Check, ChevronDown, ChevronUp, Eye, X } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type SortDirection = "asc" | "desc" | null
type SortField = "id" | "title" | "store" | "date" | "status" | "items" | null

export function ProposalsTable() {
  const [sortField, setSortField] = useState<SortField>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>(null)

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      if (sortDirection === "asc") {
        setSortDirection("desc")
      } else if (sortDirection === "desc") {
        setSortField(null)
        setSortDirection(null)
      }
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return null
    return sortDirection === "asc" ? <ChevronUp className="ml-1 h-4 w-4" /> : <ChevronDown className="ml-1 h-4 w-4" />
  }

  // Sample data
  const proposals = [
    {
      id: "1234",
      title: "Zomervoorraad Herverdeling",
      store: "Amsterdam Centrum",
      date: "24 mei 2023",
      status: "Wachtend",
      items: 24,
    },
    {
      id: "1235",
      title: "Nieuwe Collectie Verdeling",
      store: "Rotterdam Zuid",
      date: "23 mei 2023",
      status: "Wachtend",
      items: 18,
    },
    {
      id: "1236",
      title: "Seizoenswissel Voorraad",
      store: "Utrecht Centrum",
      date: "22 mei 2023",
      status: "Wachtend",
      items: 32,
    },
    {
      id: "1237",
      title: "Restvoorraad Herverdeling",
      store: "Den Haag",
      date: "21 mei 2023",
      status: "Wachtend",
      items: 15,
    },
    {
      id: "1230",
      title: "Wintercollectie Voorbereiden",
      store: "Amsterdam Zuid",
      date: "20 mei 2023",
      status: "Afgekeurd",
      items: 28,
    },
    {
      id: "1228",
      title: "Speciale Editie Verdeling",
      store: "Eindhoven",
      date: "19 mei 2023",
      status: "Goedgekeurd",
      items: 12,
    },
    {
      id: "1225",
      title: "Outlet Voorraad Herverdeling",
      store: "Groningen",
      date: "18 mei 2023",
      status: "Goedgekeurd",
      items: 45,
    },
  ]

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px] cursor-pointer" onClick={() => handleSort("id")}>
              <div className="flex items-center">ID {getSortIcon("id")}</div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort("title")}>
              <div className="flex items-center">Titel {getSortIcon("title")}</div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort("store")}>
              <div className="flex items-center">Winkel {getSortIcon("store")}</div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort("date")}>
              <div className="flex items-center">Datum {getSortIcon("date")}</div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort("status")}>
              <div className="flex items-center">Status {getSortIcon("status")}</div>
            </TableHead>
            <TableHead className="cursor-pointer text-right" onClick={() => handleSort("items")}>
              <div className="flex items-center justify-end">Items {getSortIcon("items")}</div>
            </TableHead>
            <TableHead className="w-[100px] text-right">Acties</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {proposals.map((proposal) => (
            <TableRow key={proposal.id}>
              <TableCell className="font-medium">#{proposal.id}</TableCell>
              <TableCell>
                <Link href={`/proposals/${proposal.id}`} className="hover:underline">
                  {proposal.title}
                </Link>
              </TableCell>
              <TableCell>{proposal.store}</TableCell>
              <TableCell>{proposal.date}</TableCell>
              <TableCell>
                <Badge
                  variant={
                    proposal.status === "Goedgekeurd"
                      ? "default"
                      : proposal.status === "Wachtend"
                        ? "outline"
                        : "destructive"
                  }
                >
                  {proposal.status}
                </Badge>
              </TableCell>
              <TableCell className="text-right">{proposal.items}</TableCell>
              <TableCell>
                <div className="flex justify-end gap-1">
                  {proposal.status === "Wachtend" && (
                    <>
                      <Button size="icon" variant="ghost" className="h-8 w-8 text-green-500">
                        <Check className="h-4 w-4" />
                        <span className="sr-only">Goedkeuren</span>
                      </Button>
                      <Button size="icon" variant="ghost" className="h-8 w-8 text-red-500">
                        <X className="h-4 w-4" />
                        <span className="sr-only">Afwijzen</span>
                      </Button>
                    </>
                  )}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button size="icon" variant="ghost" className="h-8 w-8">
                        <ChevronDown className="h-4 w-4" />
                        <span className="sr-only">Meer opties</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem asChild>
                        <Link href={`/proposals/${proposal.id}`}>
                          <Eye className="mr-2 h-4 w-4" />
                          Details bekijken
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>Exporteren</DropdownMenuItem>
                      <DropdownMenuItem>Notificatie versturen</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
