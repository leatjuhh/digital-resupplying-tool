import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, FileCheck, FileClock, FileX, Users } from "lucide-react"

export function DashboardStats() {
  // Deze data zou normaal gesproken via de API komen op basis van de geselecteerde periode
  const stats = {
    totaalVoorstellen: {
      waarde: 142,
      verandering: 12,
      positief: true,
    },
    inBehandeling: {
      waarde: 24,
      verandering: 7,
      positief: true,
    },
    afgekeurd: {
      waarde: 18,
      percentage: 5,
      verandering: -2,
      positief: false,
    },
    actieveWinkels: {
      waarde: 32,
      verandering: 2,
      positief: true,
    },
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Totaal Voorstellen</CardTitle>
          <FileCheck className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.totaalVoorstellen.waarde}</div>
          <div className="flex items-center text-xs text-muted-foreground">
            {stats.totaalVoorstellen.positief ? (
              <ArrowUpRight className="mr-1 h-3 w-3 text-green-500" />
            ) : (
              <ArrowDownRight className="mr-1 h-3 w-3 text-red-500" />
            )}
            {stats.totaalVoorstellen.positief ? "+" : ""}
            {stats.totaalVoorstellen.verandering}% vergeleken met vorig jaar
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">In Behandeling</CardTitle>
          <FileClock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.inBehandeling.waarde}</div>
          <div className="flex items-center text-xs text-muted-foreground">
            {stats.inBehandeling.positief ? (
              <ArrowUpRight className="mr-1 h-3 w-3" />
            ) : (
              <ArrowDownRight className="mr-1 h-3 w-3" />
            )}
            {stats.inBehandeling.positief ? "+" : ""}
            {stats.inBehandeling.verandering} sinds vorige periode
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Afgekeurd</CardTitle>
          <FileX className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.afgekeurd.waarde}</div>
          <div className="flex items-center text-xs text-muted-foreground">
            {stats.afgekeurd.percentage}% van alle voorstellen
            <span className={`ml-2 ${stats.afgekeurd.positief ? "text-green-500" : "text-red-500"}`}>
              {stats.afgekeurd.positief ? "+" : ""}
              {stats.afgekeurd.verandering}%
            </span>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Actieve Winkels</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.actieveWinkels.waarde}</div>
          <div className="flex items-center text-xs text-muted-foreground">
            {stats.actieveWinkels.positief ? "+" : ""}
            {stats.actieveWinkels.verandering} vergeleken met vorige periode
          </div>
        </CardContent>
      </Card>
    </>
  )
}
