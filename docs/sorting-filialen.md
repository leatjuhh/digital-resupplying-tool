---
title: Filialen Sortering Implementatie
category: technical
tags: [sorting, stores, backend, api]
last_updated: 2025-11-02
---

# Filialen Sortering Implementatie

## Probleem

Filialen werden niet consistent gesorteerd in voorsteltabellen, wat leidde tot verwarring bij gebruikers. De volgorde was onvoorspelbaar en vaak lexicografisch in plaats van numeriek:

**Fout (lexicografisch):** 1, 10, 100, 2, 20, 3
**Correct (numeriek):** 1, 2, 3, 10, 20, 100

## Oplossing

Implementatie van centrale sorteerlogica op de **backend** (data-bron), zodat alle API responses consistent gesorteerde data leveren.

### Voordelen Backend-First Aanpak

1. **Single Source of Truth** - Sortering gebeurt op één plek
2. **Consistentie** - Alle consumers krijgen correct gesorteerde data
3. **Performance** - Frontend hoeft niet te sorteren
4. **Onderhoudbaarheid** - Eén plek om te wijzigen bij aanpassingen

## Implementatie Details

### Backend Utilities (`backend/utils.py`)

Drie helper functies toegevoegd:

#### 1. `extract_store_code_numeric(store_id: str) -> int`

Extraheert numerieke filiaalcode uit verschillende formaten:
- Pure cijfers: `"001"` → `1`
- Met label: `"001 - Amsterdam"` → `1`
- Integer: `1` → `1`
- Invalid: `"ABC"` → `sys.maxsize` (komt onderaan)

**Edge cases:**
- Leading zeros worden correct gehandeldt: `"001"`, `"01"`, `"1"` → allemaal `1`
- Whitespace wordt gestript: `"  010  "` → `10`
- Invalid codes krijgen `sys.maxsize` en komen onderaan in sortering

#### 2. `sort_stores_by_code(stores: List, code_key='store_id', name_key='store_name') -> List`

Sorteert stores numeriek op code, met naam als tiebreaker:
- Numeriek oplopend op code (1, 2, 10, 100)
- Stores zonder geldige code onderaan
- Bij gelijke code: alfabetisch op naam

Werkt met:
- Dictionaries: `{"store_id": "001", "store_name": "Amsterdam"}`
- Objects met attributen
- Configureerbare keys voor flexibiliteit

#### 3. `sort_store_ids(store_ids: List[str]) -> List[str]`

Simpele helper voor sortering van alleen ID lists.

### API Integration (`backend/routers/pdf_ingest.py`)

**Endpoint:** `GET /api/pdf/proposals/{proposal_id}/full`

**Wijziging:**
```python
# VOOR (lexicografisch - FOUT):
for store_id in sorted(stores_inventory.keys()):
    # "1", "10", "2" volgorde

# NA (numeriek - CORRECT):
sorted_store_ids = sort_store_ids(list(stores_inventory.keys()))
for store_id in sorted_store_ids:
    # "1", "2", "10" volgorde
```

Dit zorgt ervoor dat de `stores` array in API responses altijd correct gesorteerd is.

## Testing

### Backend Tests (`backend/test_store_sorting_simple.py`)

Uitgebreide test coverage voor:

**Extract Store Code:**
- ✅ Numerieke string codes (`"001"`, `"010"`, `"100"`)
- ✅ Directe numerieke codes (`1`, `10`, `100`)
- ✅ Leading digits uit labels (`"001 - Amsterdam"` → `1`)
- ✅ Ongeldige codes retourneren `sys.maxsize`
- ✅ Whitespace handling (`"  001  "` → `1`)

**Sort Stores:**
- ✅ Basis numerieke sortering correct
- ✅ Voorkomt lexicografische bug (10 komt niet voor 2)
- ✅ Leading zeros correct behandeld
- ✅ Ongeldige codes onderaan
- ✅ Tiebreaker op naam bij gelijke codes
- ✅ Custom keys support

**Sort Store IDs:**
- ✅ Basis sortering
- ✅ Numeriek vs lexicografisch
- ✅ Lege lijst handling

**Test Resultaten:**
```
🎉 ALL TESTS PASSED! 🎉
✓ extract_store_code_numeric: 4/4 tests
✓ sort_stores_by_code: 3/3 tests  
✓ sort_store_ids: 3/3 tests
```

### Manuele Verificatie

Test met echte data in de applicatie:
1. Upload PDF's met verschillende filiaalcodes
2. Genereer voorstellen
3. Open voorstel detail pagina
4. Verifieer volgorde in tabellen: 1, 2, 3, 10, 20, 100 (niet 1, 10, 100, 2)

## Impacted Components

### Backend
- ✅ `backend/utils.py` - Nieuwe file met sorting utilities
- ✅ `backend/routers/pdf_ingest.py` - `get_proposal_with_full_inventory()` gebruikt nu `sort_store_ids()`
- ✅ `backend/test_store_sorting_simple.py` - Test suite

### Frontend
- ✅ `frontend/components/proposals/proposal-detail.tsx` - Ontvangt gesorteerde data van backend
- ✅ `frontend/components/proposals/editable-proposal-detail.tsx` - Ontvangt gesorteerde data van backend

**Geen frontend wijzigingen nodig!** Backend levert al correct gesorteerde data.

## Performance Impact

**Minimal:** O(n log n) sortering op ~10-50 stores is verwaarloosbaar (<1ms).

## Backwards Compatibility

✅ **Volledig backwards compatible**
- Bestaande API's werken ongewijzigd
- Frontend code blijft werken zonder aanpassingen
- Alleen volgorde verandert (geen breaking changes)

## Migration Path

### Voor Nieuwe Features

Gebruik altijd de utilities bij data met filialen:

```python
from utils import sort_stores_by_code, sort_store_ids

# Voor store objects/dicts:
sorted_stores = sort_stores_by_code(stores)

# Voor alleen IDs:
sorted_ids = sort_store_ids(store_ids)
```

### Voor Bestaande Endpoints

Indien meer endpoints filialen data retourneren, pas dezelfde pattern toe:
1. Import utilities
2. Sorteer voor response
3. Test met gemixte codes (1, 2, 10, 100)

## Sorteerregels Samenvatting

1. **Primair:** Numerieke waarde van filiaalcode (oplopend)
2. **Secundair:** Alfabetisch op naam (bij gelijke codes)
3. **Tertiary:** Invalid codes komen onderaan

**Voorbeelden:**

| Input | Output (Correct) |
|-------|------------------|
| 10, 2, 1, 100 | 1, 2, 10, 100 |
| 001, 010, 002 | 001, 002, 010 |
| 1, 01, 001 | Allemaal gelijk → sorteer op naam |
| 002, XXX, 001 | 001, 002, XXX |

## Future Improvements

Mogelijk uitbreidingen:
- [ ] Sorteer ook tijdens database insertion (ArtikelVoorraad)
- [ ] Voeg sortering toe aan andere endpoints indien nodig
- [ ] SQLite custom collation voor database-level sorting
- [ ] Frontend fallback sortering (defense in depth)

## References

- **Backend Utils:** `backend/utils.py`
- **API Integration:** `backend/routers/pdf_ingest.py`
- **Tests:** `backend/test_store_sorting_simple.py`
- **Issue:** Consistente filialen-sorting op code (asc) in alle tabellen

## Changelog

**2025-11-02:**
- ✅ Implementatie backend sorting utilities
- ✅ Integratie in proposal API endpoint
- ✅ Test suite met 100% pass rate
- ✅ Documentatie compleet
