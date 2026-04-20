"use client"

import { ChangeEvent } from "react"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { STORE_LIST, type StoreTotalsInput } from "@/lib/stores"

interface StoreTotalsFormProps {
  values: Partial<Record<string, string>>
  onChange: (code: string, value: string) => void
  disabled?: boolean
}

export function StoreTotalsForm({ values, onChange, disabled }: StoreTotalsFormProps) {
  return (
    <div className="grid gap-2">
      <Label>Totale winkelvoorraad per filiaal</Label>
      <p className="text-sm text-muted-foreground">
        Som van alle artikelen per winkel (niet alleen deze batch). Wordt gebruikt als
        tiebreaker bij verkoop-gelijkspel: winkel met lagere totaalvoorraad blijft receiver.
      </p>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {STORE_LIST.map((store) => {
          const inputId = `store-total-${store.code}`
          return (
            <div key={store.code} className="grid gap-1">
              <Label htmlFor={inputId} className="text-xs font-normal text-muted-foreground">
                {store.name} <span className="text-muted-foreground/70">({store.code})</span>
              </Label>
              <Input
                id={inputId}
                type="number"
                min={0}
                inputMode="numeric"
                placeholder="0"
                value={values[store.code] ?? ""}
                onChange={(event: ChangeEvent<HTMLInputElement>) =>
                  onChange(store.code, event.target.value)
                }
                disabled={disabled}
              />
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function parseStoreTotals(
  raw: Partial<Record<string, string>>,
): { totals: StoreTotalsInput; missing: string[] } {
  const totals: StoreTotalsInput = {}
  const missing: string[] = []
  for (const store of STORE_LIST) {
    const value = (raw[store.code] ?? "").trim()
    if (value === "") {
      missing.push(store.code)
      continue
    }
    const parsed = Number(value)
    if (!Number.isFinite(parsed) || parsed < 0 || !Number.isInteger(parsed)) {
      missing.push(store.code)
      continue
    }
    totals[store.code] = parsed
  }
  return { totals, missing }
}
