"use client"

import { useState } from "react"
import Link from "next/link"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronDown, ChevronUp, Eye, Search } from "lucide-react"
import { Input } from "@/components/ui/input"

interface BatchProposalsListProps {
  id: string
}

type SortDirection = "asc" | "desc" | null
type SortField = "id" | "article" | "description" | "date" | "status" | null

export function BatchProposalsList({ id }: BatchProposalsListProps) {
  const [sortField, setSortField] = useState<SortField>("id")
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc")
  const [searchQuery, setSearchQuery] = useState("")

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
      id: "423264",
      article: "TC039-04",
      description: "Brisia Peacock Top",
      supplier: "NED",
      color: "pink",
      category: "D T-Shirt Diversen",
      collection: "Voorjaar Voorkoop",
      date: "23 maart 2025",
      status: "Wachtend",
    },
    {
      id: "423265",
      article: "LR552-12",
      description: "Pipa T-Shirt",
      supplier: "NED",
      color: "black",
      category: "D T-Shirt Diversen",
      collection: "Voorjaar Voorkoop",
      date: "23 maart 2025",
      status: "Goedgekeurd",
    },
    {
      id: "423266",
      article: "BT778-05",
      description: "Liza Blouse",
      supplier: "ITA",
      color: "white",
      category: "D Blouse Lange Mouw",
      collection: "Voorjaar Voorkoop",
      date: "23 maart 2025",
      status: "Wachtend",
    },
    {
      id: "423267",
      article: "DR221-08",
      description: "Flower Summer Dress",
      supplier: "ITA",
      color: "multi",
      category: "D Jurk Kort",
      collection: "Voorjaar Voorkoop",
      date: "23 maart 2025",
      status: "Afgekeurd",
    },
    {
      id: "423268",
      article: "JK102-01",
      description: "Denim Jacket",
      supplier: "NED",
      color: "blue",
      category: "D Jasje Jeans",
      collection: "Voorjaar Voorkoop",
      date: "23 maart 2025",
      status: "Wachtend",
    },
  ]

  // Filter proposals based on search query
  const filteredProposals = proposals.filter(
    (proposal) =>
      proposal.article.toLowerCase().includes(searchQuery.toLowerCase()) ||
      proposal.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      proposal.id.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Voorstellen in deze reeks</CardTitle>
        <div className="relative w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Zoek op artikel of ID..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[80px] cursor-pointer" onClick={() => handleSort("id")}>
                  <div className="flex items-center">ID {getSortIcon("id")}</div>
                </TableHead>
                <TableHead className="cursor-pointer" onClick={() => handleSort("article")}>
                  <div className="flex items-center">Artikelcode {getSortIcon("article")}</div>
                </TableHead>
                <TableHead className="cursor-pointer" onClick={() => handleSort("description")}>
                  <div className="flex items-center">Omschrijving {getSortIcon("description")}</div>
                </TableHead>
                <TableHead>Leverancier</TableHead>
                <TableHead>Kleur</TableHead>
                <TableHead className="cursor-pointer" onClick={() => handleSort("status")}>
                  <div className="flex items-center">Status {getSortIcon("status")}</div>
                </TableHead>
                <TableHead className="text-right">Acties</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredProposals.map((proposal) => (
                <TableRow key={proposal.id}>
                  <TableCell className="font-medium">
                    <Link href={`/proposals/${proposal.id}?batchId=${id}`} className="hover:underline">
                      #{proposal.id}
                    </Link>
                  </TableCell>
                  <TableCell>{proposal.article}</TableCell>
                  <TableCell>
                    <Link href={`/proposals/${proposal.id}?batchId=${id}`} className="hover:underline">
                      {proposal.description}
                    </Link>
                  </TableCell>
                  <TableCell>{proposal.supplier}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div
                        className="h-3 w-3 rounded-full border"
                        style={{
                          backgroundColor:
                            proposal.color === "pink"
                              ? "#f9a8d4"
                              : proposal.color === "black"
                                ? "#000000"
                                : proposal.color === "white"
                                  ? "#ffffff"
                                  : proposal.color === "blue"
                                    ? "#3b82f6"
                                    : proposal.color === "multi"
                                      ? "linear-gradient(to right, #f9a8d4, #3b82f6)"
                                      : "#cccccc",
                        }}
                      />
                      {proposal.color}
                    </div>
                  </TableCell>
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
                  <TableCell>
                    <div className="flex justify-end gap-1">
                      <Button size="icon" variant="ghost" className="h-8 w-8" asChild>
                        <Link href={`/proposals/${proposal.id}?batchId=${id}`}>
                          <Eye className="h-4 w-4" />
                          <span className="sr-only">Details bekijken</span>
                        </Link>
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
