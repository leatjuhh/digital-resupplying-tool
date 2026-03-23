import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { AssignmentDetails } from "@/components/assignments/assignment-details"
import { Button } from "@/components/ui/button"
import { FeatureStatusBanner } from "@/components/ui/feature-status-banner"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function AssignmentDetailPage({ params }: { params: { id: string } }) {
  return (
    <DashboardShell>
      <div className="flex items-center">
        <Button variant="ghost" size="sm" asChild className="mr-4">
          <Link href="/assignments">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Terug
          </Link>
        </Button>
        <DashboardHeader
          heading={`Opdracht Reeks #${params.id}`}
          text="Bekijk en verwerk de herverdelingsopdrachten voor uw winkel"
        />
      </div>
      <FeatureStatusBanner description="Deze opdrachtdetailpagina gebruikt echte assignmentdata uit goedgekeurde proposals, maar blijft buiten de leidende productkern tijdens de consolidatie." />
      <AssignmentDetails id={params.id} />
    </DashboardShell>
  )
}
