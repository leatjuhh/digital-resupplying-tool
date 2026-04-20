/**
 * MC Company filialen (8 winkels) — gebruikt voor batch-aanmaak totale voorraad-invoer.
 * Filiaalcodes matchen backend BV-mapping.
 */

export interface StoreMeta {
  code: string
  name: string
}

export const STORE_LIST: readonly StoreMeta[] = [
  { code: "6", name: "Echt" },
  { code: "8", name: "Weert" },
  { code: "9", name: "Stein" },
  { code: "11", name: "Brunssum" },
  { code: "12", name: "Kerkrade" },
  { code: "13", name: "Budel" },
  { code: "31", name: "Tilburg" },
  { code: "38", name: "Tegelen" },
] as const

export type StoreTotalsInput = Record<string, number>
