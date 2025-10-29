import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bell } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function NotificationsList() {
  const notifications = [
    {
      id: 1,
      title: "Nieuw voorstel ontvangen",
      description: "Er is een nieuw herverdelingsvoorstel voor Amsterdam Centrum",
      time: "5 minuten geleden",
      unread: true,
    },
    {
      id: 2,
      title: "Deadline nadert",
      description: "3 voorstellen moeten vandaag worden beoordeeld",
      time: "2 uur geleden",
      unread: true,
    },
    {
      id: 3,
      title: "Systeem update",
      description: "Het systeem wordt vanavond om 22:00 bijgewerkt",
      time: "gisteren",
      unread: false,
    },
  ]

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base">Notificaties</CardTitle>
        <Badge>{notifications.filter((n) => n.unread).length}</Badge>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {notifications.map((notification) => (
            <div key={notification.id} className={`flex gap-4 rounded-lg p-3 ${notification.unread ? "bg-muted" : ""}`}>
              <Bell className={`h-5 w-5 ${notification.unread ? "text-primary" : "text-muted-foreground"}`} />
              <div className="space-y-1">
                <p className="text-sm font-medium leading-none">{notification.title}</p>
                <p className="text-sm text-muted-foreground">{notification.description}</p>
                <p className="text-xs text-muted-foreground">{notification.time}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
