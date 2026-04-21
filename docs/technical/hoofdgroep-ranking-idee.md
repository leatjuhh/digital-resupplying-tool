# Idee: Hoofdgroep-gebaseerde winkelranking bij herverdeling

**Status:** Geparkeerd idee — nog niet geïmplementeerd  
**Gesproken op:** 2026-04-21

---

## Achtergrond

Het algoritme gebruikt momenteel `store_total_inventory` als tiebreaker: bij gelijke verkoop krijgt de winkel met de minste *totale* voorraad voorrang als ontvanger (R3 in `_rank_receivers()`). Dit is een grove maatstaf.

Het idee is om dit te verfijnen per artikelcategorie (**hoofdgroep**): als herverdeling plaatsvindt voor b.v. schoenen, moet de winkel met de minste schoenenvoorraad voorrang krijgen — niet de winkel met de minste totale voorraad over alle categorieën.

---

## Databron

Een wekelijks automatisch gegenereerde PDF-rapportage bevat per hoofdgroep de actuele voorraad per winkel:

```
Hoofdgroep 1
  winkel 6    150
  winkel 8    200
Hoofdgroep 2
  winkel 6     80
  ...
```

- De rapportage staat beschikbaar op een **Samba share** (intern netwerk)
- Winkelcodes zijn uniform met de rest van het ERP/DRT-systeem
- Cadans: wekelijks, per herverdelingsbatch

> Hoofdgroep wordt al geëxtraheerd uit batch-PDFs en opgeslagen in `ArtikelVoorraad.pdf_metadata` — de koppeling is er al, alleen nog niet gebruikt in het algoritme.

---

## Geplande aanpak (5 componenten)

### 1. Hoofdgroep-rapport parser
`backend/pdf_extract/hoofdgroep_parser.py` (nieuw)

Parseer de PDF met `pdfplumber` (al aanwezig). Detecteer hoofdgroep-koppen en winkelrijen.  
Retourneert: `Dict[str, Dict[str, int]]` → `{hoofdgroep: {store_code: units}}`

### 2. Samba-client met handmatige fallback
`backend/samba_client.py` (nieuw)

- Configureerbaar via env vars: `SAMBA_HOST`, `SAMBA_SHARE`, `SAMBA_PATH`, `SAMBA_USER`, `SAMBA_PASS`
- Library: `smbprotocol` (pure Python)
- Retourneert `None` bij fout → handmatige upload als fallback

### 3. Algoritme-integratie
`backend/redistribution/domain.py` — voeg `hoofdgroep: Optional[str]` toe aan `ArticleStock`

`backend/redistribution/algorithm.py`:
- `load_article_data()`: lees `hoofdgroep` uit `pdf_metadata`
- Nieuwe functie `load_hoofdgroep_inventory(db, batch_id)` (parallel aan `load_store_total_inventory`)
- `_rank_receivers()`: gebruik hoofdgroep-specifieke voorraad als R3; fallback naar `store_total_inventory`

```python
hg_units = hoofdgroep_inv.get(sc, store.store_total_inventory) if hoofdgroep_inv else store.store_total_inventory
return (-store.total_sales, -series_width, -inv_total, hg_units, sc)
```

### 4. Batch-aanmaak (backend router)
Bij aanmaken batch: probeer Samba-fetch → parse → sla op in `PDFBatch.extra_data["hoofdgroep_inventory"]`.  
Fallback: handmatige PDF-upload. Bij geen van beide: algoritme valt terug op `store_total_inventory`.

### 5. Frontend
Sectie in batch-aanmaak form: "Hoofdgroep-rapportage" met knop "Ophalen van netwerk" + file upload fallback + statusindicator.

---

## Kritieke bestanden bij implementatie

| Bestand | Actie |
|---------|-------|
| `backend/pdf_extract/hoofdgroep_parser.py` | Nieuw |
| `backend/samba_client.py` | Nieuw |
| `backend/redistribution/domain.py` | Uitbreiden |
| `backend/redistribution/algorithm.py` | Uitbreiden (regels ~53–68, ~435–452) |
| `backend/routers/` (batch endpoint) | Uitbreiden |
| `frontend/` (batch creation form) | UI-uitbreiding |

**Nieuwe dependency:** `smbprotocol`

---

## Verificatie (bij implementatie)
1. Handmatige upload test-PDF → controleer `PDFBatch.extra_data["hoofdgroep_inventory"]` in DB
2. Herverdeling genereren → log toont R3 gebruikt hoofdgroep-data
3. Samba-config instellen → auto-fetch testen
4. Samba onbereikbaar → bevestig fallback naar `store_total_inventory`
