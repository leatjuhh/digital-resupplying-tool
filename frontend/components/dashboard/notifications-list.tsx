import Link from "next/link";
import { Bell } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DashboardAttentionItem } from "@/lib/api";

type NotificationsListProps = {
  items: DashboardAttentionItem[];
  isLoading?: boolean;
};

function getSeverityVariant(severity: DashboardAttentionItem["severity"]) {
  return severity === "warning" ? "destructive" : "secondary";
}

export function NotificationsList({ items, isLoading = false }: NotificationsListProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-base">Aandachtspunten</CardTitle>
          <Skeleton className="h-5 w-8 rounded-full" />
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="flex gap-4 rounded-lg border p-3">
              <Skeleton className="h-5 w-5 rounded-full" />
              <div className="w-full space-y-2">
                <Skeleton className="h-4 w-2/3" />
                <Skeleton className="h-3 w-full" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base">Aandachtspunten</CardTitle>
        <Badge variant="outline">{items.length}</Badge>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">Er zijn momenteel geen open aandachtspunten.</p>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <div key={item.id} className="flex gap-4 rounded-lg border p-3">
                <Bell className="mt-0.5 h-5 w-5 text-muted-foreground" />
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium leading-none">{item.title}</p>
                    <Badge variant={getSeverityVariant(item.severity)}>{item.severity}</Badge>
                  </div>
                  {item.href ? (
                    <Link href={item.href} className="text-sm text-muted-foreground hover:underline">
                      {item.description}
                    </Link>
                  ) : (
                    <p className="text-sm text-muted-foreground">{item.description}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
