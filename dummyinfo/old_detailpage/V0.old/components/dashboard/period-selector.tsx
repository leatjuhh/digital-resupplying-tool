"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "lucide-react"
import { format } from "date-fns"
import { nl } from "date-fns/locale"
import { Calendar as CalendarComponent } from "@/components/ui/calendar"
import { cn } from "@/lib/utils"

export function PeriodSelector() {
  const [period, setPeriod] = useState("year")
  const [comparison, setComparison] = useState("previous_year")
  const [date, setDate] = useState<Date>(new Date())

  return (
    <div className="flex flex-col sm:flex-row gap-2">
      <div className="flex items-center gap-2">
        <Select value={period} onValueChange={setPeriod}>
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Periode" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="week">Week</SelectItem>
            <SelectItem value="month">Maand</SelectItem>
            <SelectItem value="quarter">Kwartaal</SelectItem>
            <SelectItem value="year">Jaar</SelectItem>
          </SelectContent>
        </Select>

        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn("w-[150px] justify-start text-left font-normal", !date && "text-muted-foreground")}
            >
              <Calendar className="mr-2 h-4 w-4" />
              {date ? format(date, "MMMM yyyy", { locale: nl }) : <span>Selecteer datum</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <CalendarComponent mode="single" selected={date} onSelect={(date) => date && setDate(date)} initialFocus />
          </PopoverContent>
        </Popover>
      </div>

      <Select value={comparison} onValueChange={setComparison}>
        <SelectTrigger className="w-[220px]">
          <SelectValue placeholder="Vergelijk met" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="previous_period">Vorige periode</SelectItem>
          <SelectItem value="previous_year">Zelfde periode vorig jaar</SelectItem>
          <SelectItem value="no_comparison">Geen vergelijking</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
