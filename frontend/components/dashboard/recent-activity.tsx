import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export function RecentActivity() {
  const activities = [
    {
      id: 1,
      user: { name: "Marieke", initials: "MV", image: "/placeholder-user.jpg" },
      action: "heeft een voorstel goedgekeurd",
      time: "2 minuten geleden",
      proposal: "Voorstel #1234",
    },
    {
      id: 2,
      user: { name: "Jan", initials: "JB", image: "/placeholder-user.jpg" },
      action: "heeft een nieuw rapport geüpload",
      time: "45 minuten geleden",
      proposal: "Zomervoorraad 2023",
    },
    {
      id: 3,
      user: { name: "Sophie", initials: "SK", image: "/placeholder-user.jpg" },
      action: "heeft een voorstel afgewezen",
      time: "2 uur geleden",
      proposal: "Voorstel #1230",
    },
    {
      id: 4,
      user: { name: "Thomas", initials: "TD", image: "/placeholder-user.jpg" },
      action: "heeft een commentaar toegevoegd",
      time: "gisteren",
      proposal: "Voorstel #1228",
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recente Activiteit</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start gap-4">
              <Avatar className="h-8 w-8">
                <AvatarImage src={activity.user.image} alt={activity.user.name} />
                <AvatarFallback>{activity.user.initials}</AvatarFallback>
              </Avatar>
              <div className="space-y-1">
                <p className="text-sm font-medium leading-none">
                  {activity.user.name} {activity.action}
                </p>
                <p className="text-sm text-muted-foreground">{activity.proposal}</p>
                <p className="text-xs text-muted-foreground">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
