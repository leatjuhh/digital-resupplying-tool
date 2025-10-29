"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { api, type Proposal } from "@/lib/api"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronDown, ChevronUp, Eye, Search, CheckCircle2, XCircle, Clock } from "lucide-react"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"

interface BatchProposalsListProps {
  id: string
}

type SortDirection = "asc" | "desc" | null
type SortField = "id" | "article" | "description" | "status" | null

export function BatchProposalsList({ id }: BatchProposalsListProps) {
  const [sortField, setSortField] = useState<SortField>("id")
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc")
  const [searchQuery, setSearchQuery] = useState("")
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  // Fetch proposals from API
  useEffect(() => {
    async function fetchProposals() {
      try {
        setLoading(true)
        const data = await api.pdf.getBatchProposals(parseInt(id))
        setProposals(data.proposals || [])
        setError(null)
      } catch (err) {
        console.error('Failed to fetch proposals:', err)
        setError('Kon voorstellen niet ophalen')
      } finally {
        setLoading(false)
      }
    }

    fetchProposals()
  }, [id])

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

  // Filter proposals based on search query
  const filteredProposals = proposals.filter(
    (proposal) =>
      proposal.artikelnummer.toLowerCase().includes(searchQuery.toLowerCase()) ||
      proposal.article_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      proposal.id.toString().includes(searchQuery.toLowerCase()),
  )

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge className="bg-green-500"><CheckCircle2 className="mr-1 h-3 w-3" />Goedgekeurd</Badge>
      case 'rejected':
        return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />Afgekeurd</Badge>
      case 'edited':
        return <Badge variant="secondary">Aangepast</Badge>
      case 'pending':
      default:
        return <Badge variant="outline"><Clock className="mr-1 h-3 w-3" />Wachtend</Badge>
    }
  }

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
        {loading && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Voorstellen laden...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <p className="text-destructive">{error}</p>
          </div>
        )}

        {!loading && !error && filteredProposals.length === 0 && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Geen voorstellen gevonden</p>
          </div>
        )}

        {!loading && !error && filteredProposals.length > 0 && (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px] cursor-pointer" onClick={() => handleSort("id")}>
                    <div className="flex items-center">ID {getSortIcon("id")}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer" onClick={() => handleSort("article")}>
                    <div className="flex items-center">Artikelnummer {getSortIcon("article")}</div>
                  </TableHead>
                  <TableHead className="cursor-pointer" onClick={() => handleSort("description")}>
                    <div className="flex items-center">Omschrijving {getSortIcon("description")}</div>
                  </TableHead>
                  <TableHead>Winkels</TableHead>
                  <TableHead className="text-center">Bewegingen</TableHead>
                  <TableHead className="text-center">Stuks</TableHead>
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
                    <TableCell className="font-mono text-sm">{proposal.artikelnummer}</TableCell>
                    <TableCell>
                      <Link href={`/proposals/${proposal.id}?batchId=${id}`} className="hover:underline">
                        {proposal.article_name}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm text-muted-foreground">
                        {proposal.stores_affected.length} winkels
                      </div>
                    </TableCell>
                    <TableCell className="text-center">{proposal.total_moves}</TableCell>
                    <TableCell className="text-center">{proposal.total_quantity}</TableCell>
                    <TableCell>{getStatusBadge(proposal.status)}</TableCell>
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
        )}
      </CardContent>
    </Card>
  )
}
