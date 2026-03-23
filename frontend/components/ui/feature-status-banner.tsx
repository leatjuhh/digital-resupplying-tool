import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle } from "lucide-react"

type FeatureStatusBannerProps = {
  title?: string
  description: string
}

export function FeatureStatusBanner({
  title = "Niet-leidende functie",
  description,
}: FeatureStatusBannerProps) {
  return (
    <Alert className="mb-6 border-amber-300 bg-amber-50 text-amber-950 [&>svg]:text-amber-700 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-100">
      <AlertTriangle className="h-4 w-4" />
      <div className="flex items-center gap-2">
        <AlertTitle>{title}</AlertTitle>
        <Badge variant="outline" className="border-amber-500 text-amber-800 dark:border-amber-500 dark:text-amber-200">
          In consolidatie
        </Badge>
      </div>
      <AlertDescription>{description}</AlertDescription>
    </Alert>
  )
}
