"use client"

import { useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, ChevronDown, ChevronUp, ClipboardCheck, Eye } from "lucide-react"

type SortDirection = "asc" | "desc" | null
type SortField = "id" | "date" | "count" | "progress" | null

export function AssignmentsList() {
  const [sortField, setSortField] = useState<SortField>("date")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")

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

  // Sample data for assignments
  const assignments = [
    {
      id: "2025031501",
      date: "15 maart 2025",
      description: "Herverdeling voor week 11 2025",
      count: 12,
      completed: 5,
      pending: 7,
      status: "In behandeling",
    },
    {
      id: "2025030201",
      date: "2 maart 2025",
      description: "Restpartijen week 9 2025",
      count: 8,
      completed: 8,
      pending: 0,
      status: "Voltooid",
    },
    {
      id: "2025021501",
      date: "15 februari 2025",
      description: "Herverdeling voor week 7 2025",
      count: 15,
      completed: 15,
      pending: 0,
      status: "Voltooid",
    },
    {
      id: "2025020101",
      date: "1 februari 2025",
      description: "Herverdeling voor week 5 2025",
      count: 10,
      completed: 10,
      pending: 0,
      status: "Voltooid",
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Herverdelingsopdrachten</CardTitle>
        <CardDescription>Overzicht van alle opdrachten voor uw winkel</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px] cursor-pointer" onClick={() => handleSort("id")}>
                  <div className="flex items-center">Reeks ID {getSortIcon("id")}</div>
                </TableHead>
                <TableHead className="min-w-[180px]">Beschrijving</TableHead>
                <TableHead className="cursor-pointer" onClick={() => handleSort("date")}>
                  <div className="flex items-center">Datum {getSortIcon("date")}</div>
                </TableHead>
                <TableHead className="cursor-pointer text-center" onClick={() => handleSort("count")}>
                  <div className="flex items-center justify-center">Aantal {getSortIcon("count")}</div>
                </TableHead>
                <TableHead className="cursor-pointer" onClick={() => handleSort("progress")}>
                  <div className="flex items-center">Voortgang {getSortIcon("progress")}</div>
                </TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Acties</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {assignments.map((assignment) => {
                const progressPercentage = Math.round((assignment.completed / assignment.count) * 100)

                return (
                  <TableRow key={assignment.id}>
                    <TableCell className="font-medium">#{assignment.id}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <ClipboardCheck className="h-4 w-4 text-blue-500" />
                        <span>{assignment.description}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        {assignment.date}
                      </div>
                    </TableCell>
                    <TableCell className="text-center">{assignment.count}</TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span>
                            {assignment.completed} verwerkt, {assignment.pending} openstaand
                          </span>
                          <span className="font-medium">{progressPercentage}%</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-secondary">
                          <div
                            className={`h-full rounded-full ${
                              progressPercentage === 100 ? "bg-green-500" : "bg-blue-500"
                            }`}
                            style={{ width: `${progressPercentage}%` }}
                          />
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          assignment.status === "Voltooid"
                            ? "default"
                            : assignment.status === "In behandeling"
                              ? "outline"
                              : "secondary"
                        }
                      >
                        {assignment.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button asChild variant="ghost" size="sm">
                        <Link href={`/assignments/${assignment.id}`}>
                          <Eye className="mr-2 h-4 w-4" />
                          Bekijken
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
