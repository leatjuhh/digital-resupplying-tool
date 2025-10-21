import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"

export function PendingProposals() {
  const proposalSeries = [
    {
      id: "2025032301",
      title: "Herverdeling voor week 12 2025",
      date: "24 maart 2025",
      totalProposals: 42,
      assessedProposals: 12,
      nextProposalId: "423264",
    },
    {
      id: "2025031501",
      title: "Herverdeling voor week 11 2025",
      date: "15 maart 2025",
      totalProposals: 36,
      assessedProposals: 24,
      nextProposalId: "423198",
    },
    {
      id: "2025030201",
      title: "Restpartijen week 9 2025",
      date: "2 maart 2025",
      totalProposals: 15,
      assessedProposals: 8,
      nextProposalId: "423112",
    },
    {
      id: "2025021501",
      title: "Herverdeling voor week 7 2025",
      date: "15 februari 2025",
      totalProposals: 53,
      assessedProposals: 48,
      nextProposalId: "422987",
    },
  ]

  return (
    <Card>
      <CardHeader className="flex flex-row items-center">
        <div className="grid gap-1">
          <CardTitle>Wachtende Reeksen</CardTitle>
          <p className="text-sm text-muted-foreground">Reeksen met voorstellen die op beoordeling wachten</p>
        </div>
        <Button asChild variant="ghost" size="sm" className="ml-auto">
          <Link href="/proposals">Alle bekijken</Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {proposalSeries.map((series) => {
            const progressPercentage = Math.round((series.assessedProposals / series.totalProposals) * 100)

            return (
              <div key={series.id} className="flex flex-col space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium leading-none">
                      <Link href={`/proposals/batch/${series.id}`} className="hover:underline">
                        {series.title}
                      </Link>
                    </p>
                    <div className="flex items-center pt-1">
                      <p className="text-sm text-muted-foreground">{series.date}</p>
                      <span className="px-1 text-muted-foreground">·</span>
                      <p className="text-sm text-muted-foreground">{series.totalProposals} voorstellen</p>
                    </div>
                  </div>
                  <Button asChild size="sm" variant="outline" className="h-8">
                    <Link href={`/proposals/${series.nextProposalId}`}>
                      <span className="mr-1">Beoordelen</span>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span>
                      {series.assessedProposals} van {series.totalProposals} beoordeeld
                    </span>
                    <span className="font-medium">{progressPercentage}%</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-secondary">
                    <div className="h-full rounded-full bg-blue-500" style={{ width: `${progressPercentage}%` }} />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
