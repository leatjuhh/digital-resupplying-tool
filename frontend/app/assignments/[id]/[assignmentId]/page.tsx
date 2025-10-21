import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { AssignmentItemDetail } from "@/components/assignments/assignment-item-detail"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function AssignmentItemPage({ params }: { params: { id: string; assignmentId: string } }) {
  return (
    <DashboardShell>
      <div className="flex items-center">
        <Button variant="ghost" size="sm" asChild className="mr-4">
          <Link href={`/assignments/${params.id}`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Terug naar opdrachten
          </Link>
        </Button>
        <DashboardHeader heading={`Artikel Opdracht`} text="Details van de herverdelingsopdracht voor dit artikel" />
      </div>
      <AssignmentItemDetail id={params.id} assignmentId={params.assignmentId} />
    </DashboardShell>
  )
}
