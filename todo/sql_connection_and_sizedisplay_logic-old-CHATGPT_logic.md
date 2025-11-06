# DRT SQL-Based Generation — Van Oude Inzichten naar Huidige Implementatie

_Oorspronkelijk gegenereerd: 2025-11-06 22:32 (Europe/Amsterdam)_  
_Bijgewerkt met huidige implementatie: 2025-11-07 00:22 (Europe/Amsterdam)_

Dit document bevat zowel de historische context uit oude GPT-4o gesprekken over SQL-connectie en maatbalk logica, als de complete specificatie voor het implementeren van SQL-based automatische generatie in DRT v2.0+.

---

## 📋 Inhoudsopgave

1. [Historische Context (Oude GPT-4o Gesprekken)](#1-historische-context)
2. [Huidige DRT Implementatie (v1.3.0 - PDF-based)](#2-huidige-drt-implementatie)
3. [SQL-Based Generation Architectuur (v2.0 Plan)](#3-sql-based-generation-architectuur)
4. [Maatbalk Systeem](#4-maatbalk-systeem)
5. [SQL Query Specificatie](#5-sql-query-specificatie)
6. [Data Transformatie](#6-data-transformatie)
7. [Backend Implementatie](#7-backend-implementatie)
8. [Frontend Implementatie](#8-frontend-implementatie)
9. [Security & Deployment](#9-security--deployment)
10. [Testing Strategie](#10-testing-strategie)
11. [Implementation Roadmap](#11-implementation-roadmap)

---

## 1) Historische Context (Oude GPT-4o Gesprekken)

### 1.1 Context en Doelstelling

**Originele Visie:**
- Jij (Alain) bouwt een tool die voorraad herverdeelt tussen winkels van MC Company.
- De tool werkt artikel-voor-artikel: per artikel (bijv. `423423`) wordt de actuele verdeling (per maat, per filiaal) bekeken en er komt een voorstel om gaten te vullen en dubbelen af te bouwen.
- Vroege fase: input kwam uit Interfiliaalverdeling PDF-rapporten (EasyVorasWindows). Later groeide het inzicht dat SQL de primaire bron moet zijn (stabieler/zuiverder), met de PDF-layout als presentatie in de webapp.
- Een bestaand, lokaal Python-script maakt een Top 40 rapport (door EasyVoras), extraheren van artikelnummers en samenvoegen met aangeleverde artikelnummers uit winkels tot `Print_nummers.xlsx`. Dit bepaalt welke artikelnummers verder worden doorgelicht.
- Belangrijk uitgangspunt: De tool blijft mens-in-de-loop. Ook als het algoritme 99,99% goed is, kunnen gebruikers voorstellen goed- of afkeuren.

### 1.2 Belangrijke Inzichten uit Oude Gesprekken

**PDF → SQL Transitie:**
- PDF-extractie leverde incomplete & ruisgevoelige data (OCR/lay-out afhankelijk).
- SQL bleek de betrouwbare bron met rijke tabellen.
- Besluit: Primair SQL, PDF's blijven referentie voor layout/UX.

**Kern Tabellen (database `evmwin`):**
- `evlgfil` — per filiaal & artikel:
  - Maten: `VOORRAAD1…VOORRAAD13` (actuele eenheden per maatpositie)
  - Verkoop: `VERKAANT1…VERKAANT13` (aantallen verkocht per maatpositie)
- `efiliaal` — filiaalmetadata (naam, plaats, oppervlakte)
- `eplu` — Artikelstam (beschrijving, maatbalk, hoofdgroep, merk, kleur, serie, seizoen)

**Maatbalken (cruciaal):**
- `VOORRAAD1…13` zijn positie-kolommen; betekenis verschilt per maatbalk.
- Voorbeeld (artikel `423423`): maatbalk 20 => `VOORRAAD1=32, …, VOORRAAD9=48`.
- Voor nu bekende mappings:
  - 1 — "XS t/m XXL": `[None, XS, S, M, L, XL, XXL, None…]`
  - 2 — "34 t/m 48": `[34, 36, 38, 40, 42, 44, 46, 48, None…]`
  - 7 — "Geen maat": artikelen zonder maatgrid
  - 9 — "Geen maat (alleen --)": `VOORRAAD1="--", rest None`
  - 10 — "XXS-XXXL": `[XXS, XS, S, M, L, XL, XXL, XXXL, None…]`
  - 20 — "32 t/m 48": `[32, 34, 36, 38, 40, 42, 44, 46, 48, None…]`
  - 21 — "One Size": `VOORRAAD1="One Size"`

**BV-grenzen:**
- Lumitex BV: filialen 6–13 (Echt…Budel)
- Partners BV: filialen 31–38 (Tilburg…Tegelen)
- Geen cross-BV verplaatsingen in v0.1 (hard business-rule).

### 1.3 Basis SQL Query (uit oude gesprekken)

```sql
-- Basis query voor één artikel
SELECT
  l.FILIAALNUMMER, f.NAAM AS FILIAALNAAM, l.VOLGNUMMER,
  l.VOORRAAD1, l.VOORRAAD2, l.VOORRAAD3, l.VOORRAAD4, l.VOORRAAD5,
  l.VOORRAAD6, l.VOORRAAD7, l.VOORRAAD8, l.VOORRAAD9, l.VOORRAAD10,
  l.VOORRAAD11, l.VOORRAAD12, l.VOORRAAD13,
  l.VERKAANT1, l.VERKAANT2, l.VERKAANT3, l.VERKAANT4, l.VERKAANT5,
  l.VERKAANT6, l.VERKAANT7, l.VERKAANT8, l.VERKAANT9, l.VERKAANT10,
  l.VERKAANT11, l.VERKAANT12, l.VERKAANT13
FROM evlgfil l
LEFT JOIN efiliaal f ON f.FILIAALNUMMER = l.FILIAALNUMMER
WHERE l.VOLGNUMMER = 423423;
```

---

## 2) Huidige DRT Implementatie (v1.3.0 - PDF-based)

### 2.1 Overzicht

**Huidige workflow:**
```
[PDF Upload] → [PDF Parser] → [ArtikelVoorraad records] → [Algoritme] → [Proposals] → [UI Review]
```

**Technologie:**
- Backend: FastAPI, Python 3.11+, SQLAlchemy
- Frontend: Next.js 14, TypeScript, Tailwind CSS
- Database: SQLite (database.db)

### 2.2 Huidige Database Schema

**PDFBatch tabel:**
```python
class PDFBatch(Base):
    id: int (PK)
    naam: str
    status: str  # 'PENDING', 'SUCCESS', 'FAILED', 'PARTIAL_SUCCESS'
    pdf_count: int
    processed_count: int
    created_at: DateTime
```

**ArtikelVoorraad tabel (huidig):**
```python
class ArtikelVoorraad(Base):
    id: int (PK)
    batch_id: int (FK -> pdf_batches.id)
    volgnummer: str (artikelnummer)
    omschrijving: str
    filiaal_code: str
    filiaal_naam: str
    maat: str  # Één maat per record!
    voorraad: int
    verkocht: int  # Alleen in eerste record per filiaal
    pdf_metadata: JSON
    created_at: DateTime
```

**Proposal tabel:**
```python
class Proposal(Base):
    id: int (PK)
    pdf_batch_id: int (FK -> pdf_batches.id)
    artikelnummer: str
    article_name: str
    moves: JSON  # [{"size": "M", "from_store": "001", "to_store": "002", "qty": 5}]
    total_moves: int
    total_quantity: int
    status: str  # 'pending', 'approved', 'rejected', 'edited'
    reason: Text
    applied_rules: JSON
    optimization_applied: str
    stores_affected: JSON
    created_at: DateTime
    reviewed_at: DateTime
    rejection_reason: Text
```

### 2.3 Huidige PDF Ingest Flow

**Endpoint:** `POST /api/pdf/ingest`

**Process:**
1. Upload PDF(s) → save to `backend/uploads/pdf_batches/batch_{id}/`
2. Parse PDF met `pdf_extract.pipeline.parse_pdf_to_records()`
3. Extract metadata (Volgnummer, Omschrijving, etc.)
4. Extract voorraad per filiaal per maat
5. Bereken verkocht per filiaal (som van VERKAANT kolommen)
6. Save naar `ArtikelVoorraad` records (één per maat per filiaal)
7. Trigger `generate_redistribution_proposals_for_batch()`
8. Return batch_id

**Belangrijk Detail: Verkocht Opslag**
```python
# Alleen EERSTE record per filiaal krijgt verkocht waarde
first_record_for_filiaal = True
for maat, voorraad in voorraad_per_maat.items():
    if voorraad > 0 or (verkocht > 0 and first_record_for_filiaal):
        record = ArtikelVoorraad(
            # ...
            verkocht=verkocht if first_record_for_filiaal else 0
        )
        first_record_for_filiaal = False
```

### 2.4 Huidige Algoritme Werking

**Load Article Data:** `backend/redistribution/algorithm.py`

```python
def load_article_data(db: Session, volgnummer: str, batch_id: int) -> ArticleStock:
    """
    Laad artikel voorraad data uit database (ArtikelVoorraad records)
    """
    records = db.query(ArtikelVoorraad).filter(
        ArtikelVoorraad.volgnummer == volgnummer,
        ArtikelVoorraad.batch_id == batch_id
    ).all()
    
    # Groepeer per winkel
    # Detecteer maatreeksen
    # Bereken metrics
    # Return ArticleStock object
```

**Kernpunt:** Het algoritme leest uit `ArtikelVoorraad` tabel en verwacht geen specifieke bron (PDF of SQL). Dit blijft ongewijzigd!

### 2.5 Huidige Frontend

**Upload Pagina:** `http://localhost:3000/uploads`

**Twee tabs:**
1. **"Automatisch Genereren"** - Momenteel alleen simulatie
2. **"Handmatig Uploaden"** - PDF upload (werkend)

**Proposal Weergave:** `http://localhost:3000/proposals/{id}?batchId={batchId}`
- Matrix view (filialen × maten)
- Vergelijking tab (current vs proposed)
- Approve/Reject/Edit functionaliteit

---

## 3) SQL-Based Generation Architectuur (v2.0 Plan)

### 3.1 Kernidee

**Strategie:** SQL data transformeren naar DEZELFDE `ArtikelVoorraad` structuur als PDF data, zodat de rest van het systeem identiek blijft werken.

```
┌─────────────────────────────────────────────────────────┐
│         EasyVorasWindows SQL Database (evmwin)          │
│  Tables: evlgfil, efiliaal, eplu                        │
└─────────────────────────────────────────────────────────┘
                        ↓ (SSH + MySQL)
┌─────────────────────────────────────────────────────────┐
│              SQL Extractor Service (NIEUW)              │
│  - Connect via SSH tunnel                               │
│  - Query met alle Interfiliaalverdeling velden          │
│  - Fetch maatbalk_id uit eplu                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│            Maatbalk Mapping System (NIEUW)              │
│  - Lookup maatbalk_id in maatbalk_mappings tabel        │
│  - Referentie: todo/maatbalk_mapping_voras.png          │
│  - Learning: PDF uploads "trainen" nieuwe maatbalken    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Data Transformer (NIEUW)                   │
│  - VOORRAAD1-13 → {maat: qty} dmv maatbalk mapping      │
│  - VERKAANT1-13 → totaal verkocht per filiaal           │
│  - Create ArtikelVoorraad records (+ source='sql')      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│       ArtikelVoorraad Tabel (+ nieuwe kolommen)         │
│  + source: VARCHAR(10) - 'pdf' of 'sql'                │
│  + maatbalk_id: INTEGER - voor traceerbaarheid          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│         Bestaand Herverdelingsalgoritme                 │
│  (GEEN WIJZIGINGEN - werkt met beide bronnen!)          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Proposals & UI                             │
│  (IDENTIEK - zelfde weergave als PDF-based)             │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Dual Mode Operation

**Beide systemen blijven parallel werken:**

| Aspect | PDF Upload | SQL Extract |
|--------|-----------|-------------|
| **Trigger** | Handmatig via UI | Automatisch knop in UI |
| **Bron** | PDF bestanden | EasyVoras SQL database |
| **Input** | Upload bestanden | Lijst artikelnummers (tekst) |
| **Batch naam** | Automatisch of custom | "Herverdeling week XX YYYY" |
| **ArtikelVoorraad.source** | `'pdf'` | `'sql'` |
| **Algoritme** | Identiek | Identiek |
| **Proposal weergave** | Identiek | Identiek |
| **UI Indicator** | Kolom in reekslijst | Kolom in reekslijst |

**UI Overzicht:**
```
┌──────────────────────────────────────────────────────────┐
│  Reeksen Overzicht                                        │
├──────────────────────────────────────────────────────────┤
│  Reeks                    | Bron | Artikelen | Voorstell.│
│  ───────────────────────────────────────────────────────│
│  Herverdeling week 45 2025 | SQL  |    42    |    38    │
│  Handmatige upload 05-11   | PDF  |    15    |    12    │
│  Herverdeling week 44 2025 | SQL  |    50    |    45    │
└──────────────────────────────────────────────────────────┘
```

---

## 4) Maatbalk Systeem

### 4.1 Screenshot Referentie

**Bestand:** `todo/maatbalk_mapping_voras.png`

Dit is een screenshot uit EasyVorasWindows die de maatbalk configuratie toont. Deze mapping is cruciaal voor het correct interpreteren van `VOORRAAD1-13` posities.

### 4.2 Database Tabel: maatbalk_mappings (NIEUW)

```sql
CREATE TABLE maatbalk_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    maatbalk_id INTEGER UNIQUE NOT NULL,
    maatbalk_naam VARCHAR(100),
    positie_1 VARCHAR(20),
    positie_2 VARCHAR(20),
    positie_3 VARCHAR(20),
    positie_4 VARCHAR(20),
    positie_5 VARCHAR(20),
    positie_6 VARCHAR(20),
    positie_7 VARCHAR(20),
    positie_8 VARCHAR(20),
    positie_9 VARCHAR(20),
    positie_10 VARCHAR(20),
    positie_11 VARCHAR(20),
    positie_12 VARCHAR(20),
    positie_13 VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'manual'  -- 'manual', 'pdf_learned', 'config'
);
```

### 4.3 Initiële Maatbalk Data

**Seed script:** `backend/seed_maatbalk_mappings.py`

```python
INITIAL_MAATBALK_DATA = [
    {
        'maatbalk_id': 1,
        'maatbalk_naam': 'XS t/m XXL',
        'positions': [None, 'XS', 'S', 'M', 'L', 'XL', 'XXL', None, None, None, None, None, None]
    },
    {
        'maatbalk_id': 2,
        'maatbalk_naam': '34 t/m 48',
        'positions': ['34', '36', '38', '40', '42', '44', '46', '48', None, None, None, None, None]
    },
    {
        'maatbalk_id': 7,
        'maatbalk_naam': 'Geen maat',
        'positions': ['--', None, None, None, None, None, None, None, None, None, None, None, None]
    },
    {
        'maatbalk_id': 9,
        'maatbalk_naam': 'Geen maat (alleen --)',
        'positions': ['--', None, None, None, None, None, None, None, None, None, None, None, None]
    },
    {
        'maatbalk_id': 10,
        'maatbalk_naam': 'XXS-XXXL',
        'positions': ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', None, None, None, None, None]
    },
    {
        'maatbalk_id': 20,
        'maatbalk_naam': '32 t/m 48',
        'positions': ['32', '34', '36', '38', '40', '42', '44', '46', '48', None, None, None, None]
    },
    {
        'maatbalk_id': 21,
        'maatbalk_naam': 'One Size',
        'positions': ['One Size', None, None, None, None, None, None, None, None, None, None, None, None]
    }
]

def seed_maatbalk_mappings(db: Session):
    """Seed initial maatbalk mappings into database"""
    for data in INITIAL_MAATBALK_DATA:
        mapping = MaatbalkMapping(
            maatbalk_id=data['maatbalk_id'],
            maatbalk_naam=data['maatbalk_naam'],
            source='manual'
        )
        
        # Set position columns
        for i, pos in enumerate(data['positions'], start=1):
            setattr(mapping, f'positie_{i}', pos)
        
        db.add(mapping)
    
    db.commit()
```

### 4.4 Maatbalk Learning via PDF

**Concept:** PDF uploads "trainen" nieuwe maatbalken

```python
def learn_maatbalk_from_pdf(pdf_data: dict, maatbalk_id: int, db: Session):
    """
    Extract maatbalk mapping uit PDF header en save naar database
    """
    # Check of al bekend
    existing = db.query(MaatbalkMapping).filter_by(maatbalk_id=maatbalk_id).first()
    if existing:
        return  # Al bekend
    
    # Extract maat labels uit PDF tabel header
    size_labels = extract_size_labels_from_pdf_header(pdf_data)
    
    if not size_labels:
        logger.warning(f"Could not extract size labels for maatbalk {maatbalk_id}")
        return
    
    # Create nieuwe mapping
    mapping = MaatbalkMapping(
        maatbalk_id=maatbalk_id,
        maatbalk_naam=f"Auto-learned from PDF",
        source='pdf_learned'
    )
    
    for i, label in enumerate(size_labels[:13], start=1):
        setattr(mapping, f'positie_{i}', label if label else None)
    
    db.add(mapping)
    db.commit()
    
    logger.info(f"Learned new maatbalk {maatbalk_id} from PDF: {size_labels}")
```

### 4.5 Error Handling: Onbekende Maatbalk

```python
def get_maatbalk_mapping(maatbalk_id: int, db: Session) -> dict:
    """
    Haal maatbalk mapping op uit database
    
    Returns:
        Dict met 'error' flag en data/message
    """
    mapping = db.query(MaatbalkMapping).filter_by(maatbalk_id=maatbalk_id).first()
    
    if not mapping:
        return {
            'error': True,
            'maatbalk_id': maatbalk_id,
            'message': f'ONBEKENDE MAATBALK {maatbalk_id}',
            'instruction': 'UPLOAD EERST EEN PDF MET DEZE MAATBALK OM HEM AAN TE MAKEN',
            'positions': []
        }
    
    # Haal posities op
    positions = [
        getattr(mapping, f'positie_{i}', None)
        for i in range(1, 14)
    ]
    
    return {
        'error': False,
        'maatbalk_id': maatbalk_id,
        'maatbalk_naam': mapping.maatbalk_naam,
        'positions': positions,
        'source': mapping.source
    }
```

**UI Weergave bij onbekende maatbalk:**
```
┌──────────────────────────────────────────────────────────┐
│  ⚠ Fout bij artikel 424789                               │
│                                                           │
│  ONBEKENDE MAATBALK 15                                   │
│                                                           │
│  Dit artikel gebruikt een maatbalk die nog niet in DRT   │
│  is gedefinieerd. Upload eerst een Interfiliaalverdeling │
│  PDF rapport van dit artikel om de maatbalk te leren.    │
│                                                           │
│  [Upload PDF voor Artikel 424789]                        │
└──────────────────────────────────────────────────────────┘
```

---

## 5) SQL Query Specificatie

### 5.1 Volledige Query (Alle Interfiliaalverdeling Velden)

**Doel:** Haal ALLE velden op die nodig zijn voor de Interfiliaalverdeling weergave, inclusief metadata die zichtbaar is in de PDF (Leverancier, Hoofdgroep, Kleur, etc.).

```sql
SELECT
  -- Basis identifiers
  l.VOLGNUMMER,
  l.FILIAALNUMMER,
  
  -- Filiaal informatie
  f.NAAM AS FILIAALNAAM,
  f.PLAATS,
  f.OPPERVLAKTE,
  
  -- Artikel metadata (KRITIEK: inclusief MAATBALK)
  p.OMSCHRIJVING1 AS OMSCHRIJVING,
  p.LEVERANCIER,
  p.HOOFDGROEP,
  p.KLEUR,
  p.SERIE,
  p.SEIZOEN,
  p.MERK,
  p.MAATBALK AS MAATBALK_ID,  -- ESSENTIEEL voor maat interpretatie!
  
  -- Voorraad per maatpositie (1-13)
  l.VOORRAAD1, l.VOORRAAD2, l.VOORRAAD3, l.VOORRAAD4,
  l.VOORRAAD5, l.VOORRAAD6, l.VOORRAAD7, l.VOORRAAD8,
  l.VOORRAAD9, l.VOORRAAD10, l.VOORRAAD11, l.VOORRAAD12, l.VOORRAAD13,
  
  -- Verkocht per maatpositie (1-13)
  l.VERKAANT1, l.VERKAANT2, l.VERKAANT3, l.VERKAANT4,
  l.VERKAANT5, l.VERKAANT6, l.VERKAANT7, l.VERKAANT8,
  l.VERKAANT9, l.VERKAANT10, l.VERKAANT11, l.VERKAANT12, l.VERKAANT13
  
FROM evlgfil l
LEFT JOIN efiliaal f ON f.FILIAALNUMMER = l.FILIAALNUMMER
LEFT JOIN eplu p ON p.VOLGNUMMER = l.VOLGNUMMER
WHERE l.VOLGNUMMER IN (:volgnummer_list);
```

**Belangrijke Note:** Als `eplu` tabel leeg is, moet er een fallback strategie zijn:
- Check alternatieve stamtabellen (bijv. `evplu`, `evorar`)
- Gebruik maatbalk configuratie bestand
- Maatbalk override via API parameter

### 5.2 Parameterized Query (Python/PyMySQL)

```python
def fetch_articles_from_evoras(volgnummer_list: List[str], conn) -> List[Dict]:
    """
    Fetch artikel data voor meerdere volgnummers
    """
    placeholders = ','.join(['%s'] * len(volgnummer_list))
    
    query = f"""
    SELECT
      l.VOLGNUMMER,
      l.FILIAALNUMMER,
      f.NAAM AS FILIAALNAAM,
      f.PLAATS,
      p.OMSCHRIJVING1 AS OMSCHRIJVING,
      p.LEVERANCIER,
      p.HOOFDGROEP,
      p.KLEUR,
      p.MAATBALK AS MAATBALK_ID,
      l.VOORRAAD1, l.VOORRAAD2, l.VOORRAAD3, l.VOORRAAD4,
      l.VOORRAAD5, l.VOORRAAD6, l.VOORRAAD7, l.VOORRAAD8,
      l.VOORRAAD9, l.VOORRAAD10, l.VOORRAAD11, l.VOORRAAD12, l.VOORRAAD13,
      l.VERKAANT1, l.VERKAANT2, l.VERKAANT3, l.VERKAANT4,
      l.VERKAANT5, l.VERKAANT6, l.VERKAANT7, l.VERKAANT8,
      l.VERKAANT9, l.VERKAANT10, l.VERKAANT11, l.VERKAANT12, l.VERKAANT13
    FROM evlgfil l
    LEFT JOIN efiliaal f ON f.FILIAALNUMMER = l.FILIAALNUMMER
    LEFT JOIN eplu p ON p.VOLGNUMMER = l.VOLGNUMMER
    WHERE l.VOLGNUMMER IN ({placeholders})
    """
    
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, volgnummer_list)
        results = cursor.fetchall()
    
    return results
```

### 5.3 Fallback Query (als eplu leeg is)

```python
def try_alternative_metadata_sources(volgnummer: str, conn) -> Optional[Dict]:
    """
    Probeer alternatieve bronnen voor artikel metadata
    """
    # Optie 1: Check evplu tabel
    try:
        query = "SELECT MAATBALK, OMSCHRIJVING1 FROM evplu WHERE VOLGNUMMER = %s"
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, (volgnummer,))
            result = cursor.fetchone()
            if result and result.get('MAATBALK'):
                return result
    except Exception as e:
        logger.warning(f"evplu query failed: {e}")
    
    # Optie 2: Gebruik config file mapping
    maatbalk_config = load_maatbalk_config()  # artikel ranges → maatbalk
    maatbalk_id = maatbalk_config.get_maatbalk_for_article(volgnummer)
    
    if maatbalk_id:
        return {'MAATBALK': maatbalk_id, 'OMSCHRIJVING1': None}
    
    return None
```

---

## 6) Data Transformatie

### 6.1 Van SQL naar ArtikelVoorraad Records

**Input:** SQL query resultaat (dict per row)  
**Output:** List van ArtikelVoorraad records

```python
def transform_sql_row_to_voorraad_records(
    sql_row: Dict,
    batch_id: int,
    maatbalk_mapping: Dict,
    db: Session
) -> List[ArtikelVoorraad]:
    """
    Transform één SQL row naar meerdere ArtikelVoorraad records (één per maat)
    """
    records = []
    
    # Extract basics
    volgnummer = sql_row['VOLGNUMMER']
    filiaal_code = str(sql_row['FILIAALNUMMER'])
    filiaal_naam = sql_row.get('FILIAALNAAM', '')
    
    # Extract voorraad en verkocht arrays
    voorraad_values = [sql_row.get(f'VOORRAAD{i}', 0) for i in range(1, 14)]
    verkaant_values = [sql_row.get(f'VERKAANT{i}', 0) for i in range(1, 14)]
    
    # Bereken totaal verkocht voor dit filiaal
    total_verkocht = sum(verkaant_values)
    
    # Metadata voor pdf_metadata veld
    metadata = {
        'leverancier': sql_row.get('LEVERANCIER'),
        'hoofdgroep': sql_row.get('HOOFDGROEP'),
        'kleur': sql_row.get('KLEUR'),
        'serie': sql_row.get('SERIE'),
        'plaats': sql_row.get('PLAATS'),
        'maatbalk_id': sql_row.get('MAATBALK_ID')
    }
    
    # Voor elke positie: als maat label bestaat EN voorraad > 0
    first_record = True
    for idx, (maat_label, voorraad, verkocht_per_maat) in enumerate(
        zip(maatbalk_mapping['positions'], voorraad_values, verkaant_values),
        start=1
    ):
        # Skip als geen maat label
        if maat_label is None:
            continue
        
        # Create record als voorraad > 0, OF als het eerste record is met verkocht > 0
        if voorraad > 0 or (first_record and total_verkocht > 0):
            record = ArtikelVoorraad(
                batch_id=batch_id,
                volgnummer=volgnummer,
                omschrijving=sql_row.get('OMSCHRIJVING', ''),
                filiaal_code=filiaal_code,
                filiaal_naam=filiaal_naam,
                maat=maat_label,
                voorraad=voorraad,
                verkocht=total_verkocht if first_record else 0,  # Alleen eerste record!
                source='sql',
                maatbalk_id=sql_row.get('MAATBALK_ID'),
                pdf_metadata=metadata
            )
            records.append(record)
            first_record = False
    
    return records
```

### 6.2 Complete Transformer Class

```python
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class SQLDataTransformer:
    """
    Transform SQL data naar ArtikelVoorraad records
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def transform_batch(
        self,
        sql_rows: List[Dict],
        batch_id: int
    ) -> tuple[List[ArtikelVoorraad], List[str]]:
        """
        Transform alle SQL rows naar ArtikelVoorraad records
        
        Returns:
            Tuple van (records, errors)
        """
        all_records = []
        errors = []
        
        for row in sql_rows:
            try:
                # Haal maatbalk ID op
                maatbalk_id = row.get('MAATBALK_ID')
                
                if not maatbalk_id:
                    errors.append(
                        f"Artikel {row['VOLGNUMMER']}: Geen maatbalk_id gevonden"
                    )
                    continue
                
                # Haal maatbalk mapping op
                mapping = self.get_maatbalk_mapping(maatbalk_id)
                
                if mapping.get('error'):
                    errors.append(
                        f"Artikel {row['VOLGNUMMER']}: {mapping['message']}"
                    )
                    continue
                
                # Transform row naar records
                records = transform_sql_row_to_voorraad_records(
                    row, batch_id, mapping, self.db
                )
                
                all_records.extend(records)
                
            except Exception as e:
                logger.error(f"Error transforming row {row.get('VOLGNUMMER')}: {e}")
                errors.append(
                    f"Artikel {row.get('VOLGNUMMER', 'UNKNOWN')}: {str(e)}"
                )
        
        return all_records, errors
    
    def get_maatbalk_mapping(self, maatbalk_id: int) -> Dict:
        """Haal maatbalk mapping op (zie sectie 4.5)"""
        return get_maatbalk_mapping(maatbalk_id, self.db)
```

---

## 7) Backend Implementatie

### 7.1 SQL Connector Service

**Nieuw bestand:** `backend/sql_extract/evoras_connector.py`

```python
"""
EasyVoras SQL Connector
Manages SSH tunnel + MySQL connection to EasyVorasWindows database
"""

import paramiko
import pymysql
from typing import List, Dict, Optional
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class EvorasConnector:
    """
    SSH + MySQL connector voor EasyVorasWindows database
    """
    
    def __init__(self):
        self.ssh_client = None
        self.mysql_conn = None
        self.connected = False
        
    def connect(self):
        """
        Maak SSH tunnel + MySQL connectie
        """
        try:
            # SSH connectie
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh_config = {
                'hostname': os.getenv('EVORAS_SSH_HOST'),
                'username': os.getenv('EVORAS_SSH_USER'),
                'port': int(os.getenv('EVORAS_SSH_PORT', '22'))
            }
            
            # Use key or password
            key_path = os.getenv('EVORAS_SSH_KEY_PATH')
            if key_path and os.path.exists(key_path):
                ssh_config['key_filename'] = key_path
            else:
                ssh_config['password'] = os.getenv('EVORAS_SSH_PASSWORD')
            
            self.ssh_client.connect(**ssh_config)
            logger.info("SSH connection established")
            
            # MySQL connectie
            self.mysql_conn = pymysql.connect(
                host=os.getenv('EVORAS_MYSQL_HOST', 'localhost'),
                port=int(os.getenv('EVORAS_MYSQL_PORT', '3306')),
                user=os.getenv('EVORAS_MYSQL_USER'),
                password=os.getenv('EVORAS_MYSQL_PASSWORD'),
                database=os.getenv('EVORAS_MYSQL_DATABASE', 'evmwin'),
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=30
            )
            
            self.connected = True
            logger.info("MySQL connection established to evmwin database")
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.close()
            raise
    
    def fetch_articles(self, volgnummer_list: List[str]) -> List[Dict]:
        """
        Fetch artikel data voor meerdere volgnummers
        """
        if not self.connected:
            self.connect()
        
        if not volgnummer_list:
            return []
        
        placeholders = ','.join(['%s'] * len(volgnummer_list))
        
        query = f"""
        SELECT
          l.VOLGNUMMER,
          l.FILIAALNUMMER,
          f.NAAM AS FILIAALNAAM,
          f.PLAATS,
          p.OMSCHRIJVING1 AS OMSCHRIJVING,
          p.LEVERANCIER,
          p.HOOFDGROEP,
          p.KLEUR,
          p.SERIE,
          p.MAATBALK AS MAATBALK_ID,
          l.VOORRAAD1, l.VOORRAAD2, l.VOORRAAD3, l.VOORRAAD4,
          l.VOORRAAD5, l.VOORRAAD6, l.VOORRAAD7, l.VOORRAAD8,
          l.VOORRAAD9, l.VOORRAAD10, l.VOORRAAD11, l.VOORRAAD12, l.VOORRAAD13,
          l.VERKAANT1, l.VERKAANT2, l.VERKAANT3, l.VERKAANT4,
          l.VERKAANT5, l.VERKAANT6, l.VERKAANT7, l.VERKAANT8,
          l.VERKAANT9, l.VERKAANT10, l.VERKAANT11, l.VERKAANT12, l.VERKAANT13
        FROM evlgfil l
        LEFT JOIN efiliaal f ON f.FILIAALNUMMER = l.FILIAALNUMMER
        LEFT JOIN eplu p ON p.VOLGNUMMER = l.VOLGNUMMER
        WHERE l.VOLGNUMMER IN ({placeholders})
        """
        
        try:
            with self.mysql_conn.cursor() as cursor:
                cursor.execute(query, volgnummer_list)
                results = cursor.fetchall()
            
            logger.info(f"Fetched {len(results)} records for {len(volgnummer_list)} articles")
            return results
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def close(self):
        """Cleanup connections"""
        if self.mysql_conn:
            try:
                self.mysql_conn.close()
                logger.info("MySQL connection closed")
            except:
                pass
        
        if self.ssh_client:
            try:
                self.ssh_client.close()
                logger.info("SSH connection closed")
            except:
                pass
        
        self.connected = False

@contextmanager
def evoras_connection():
    """Context manager voor EasyVoras connectie"""
    connector = EvorasConnector()
    try:
        connector.connect()
        yield connector
    finally:
        connector.close()
```

### 7.2 SQL Ingest Router

**Nieuw bestand:** `backend/routers/sql_ingest.py`

```python
"""
SQL Ingest API Router
Handles SQL-based article extraction from EasyVorasWindows
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging

from database import get_db
from db_models import PDFBatch, PDFParseLog
from sql_extract.evoras_connector import evoras_connection
from sql_extract.transformer import SQLDataTransformer
from redistribution.algorithm import generate_redistribution_proposals_for_batch

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sql-ingest", tags=["sql-ingest"])


class SQLGenerateRequest(BaseModel):
    batch_name: str
    volgnummer_list: List[str]
    maatbalk_overrides: Optional[Dict[str, int]] = {}


@router.post("/generate")
async def generate_from_sql(
    request: SQLGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Genereer batch uit SQL database
    
    Args:
        request: SQLGenerateRequest met batch_name en volgnummer_list
        db: Database session
        
    Returns:
        JSON met batch_id, status, en statistieken
    """
    logger.info(f"[SQL_GENERATE_START] {len(request.volgnummer_list)} articles requested")
    
    # 1. Create batch
    batch = PDFBatch(
        naam=request.batch_name,
        status="PENDING",
        pdf_count=0,  # SQL heeft geen PDFs
        processed_count=0
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    batch_id = batch.id
    
    try:
        # 2. Connect to EasyVoras & Fetch data
        logger.info(f"[SQL_CONNECT] Connecting to EasyVoras database")
        
        with evoras_connection() as connector:
            sql_rows = connector.fetch_articles(request.volgnummer_list)
        
        if not sql_rows:
            raise HTTPException(
                status_code=404,
                detail="No data found for provided articles"
            )
        
        logger.info(f"[SQL_FETCH] Retrieved {len(sql_rows)} rows from database")
        
        # 3. Transform to ArtikelVoorraad
        transformer = SQLDataTransformer(db)
        voorraad_records, errors = transformer.transform_batch(sql_rows, batch_id)
        
        if errors:
            # Log errors
            for error in errors:
                log_entry = PDFParseLog(
                    batch_id=batch_id,
                    phase="SQL_TRANSFORM",
                    level="ERROR",
                    message=error,
                    extra_data={}
                )
                db.add(log_entry)
            db.commit()
        
        if not voorraad_records:
            batch.status = "FAILED"
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"No valid records created. Errors: {errors}"
            )
        
        # 4. Save to database
        for record in voorraad_records:
            db.add(record)
        db.commit()
        
        logger.info(f"[SQL_SAVE] Saved {len(voorraad_records)} ArtikelVoorraad records")
        
        # 5. Update batch status
        unique_articles = len(set(r.volgnummer for r in voorraad_records))
        batch.processed_count = unique_articles
        batch.status = "PARTIAL_SUCCESS" if errors else "SUCCESS"
        db.commit()
        
        # 6. Generate proposals
        logger.info(f"[SQL_PROPOSALS] Generating redistribution proposals")
        proposals = generate_redistribution_proposals_for_batch(db, batch_id)
        
        logger.info(f"[SQL_COMPLETE] Success: {unique_articles} articles, {len(proposals)} proposals")
        
        return {
            "batch_id": batch_id,
            "status": batch.status,
            "articles_requested": len(request.volgnummer_list),
            "articles_processed": unique_articles,
            "proposals_generated": len(proposals),
            "records_created": len(voorraad_records),
            "errors": errors if errors else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SQL_ERROR] Failed: {e}", exc_info=True)
        batch.status = "FAILED"
        db.commit()
        
        # Log error
        log_entry = PDFParseLog(
            batch_id=batch_id,
            phase="SQL_GENERATION",
            level="ERROR",
            message=str(e),
            extra_data={}
        )
        db.add(log_entry)
        db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))
```

### 7.3 Database Schema Updates

**Migratie script:** `backend/migrate_add_sql_support.py`

```python
"""
Add SQL support columns to ArtikelVoorraad
"""

from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        # Add source column
        conn.execute(text("""
            ALTER TABLE artikel_voorraad
            ADD COLUMN source VARCHAR(10) DEFAULT 'pdf'
        """))
        
        # Add maatbalk_id column
        conn.execute(text("""
            ALTER TABLE artikel_voorraad
            ADD COLUMN maatbalk_id INTEGER NULL
        """))
        
        conn.commit()
        print("✓ Migration complete: added source and maatbalk_id columns")

if __name__ == "__main__":
    migrate()
```

---

## 8) Frontend Implementatie

### 8.1 Generate Component Update

**Update bestand:** `frontend/components/uploads/generate-proposals.tsx`

```typescript
// Replace simulation met echte API call

const [articleCodes, setArticleCodes] = useState('');

const generateProposals = async () => {
  setGenerating(true);
  setCompleted(false);
  setProgress(0);
  setStage("Voorbereiden...");

  try {
    // Parse artikel input
    const volgnummers = articleCodes
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0 && /^\d+$/.test(line));

    if (volgnummers.length === 0) {
      toast({
        title: "Geen artikelen",
        description: "Voer minimaal één geldig artikelnummer in.",
        variant: "destructive"
      });
      setGenerating(false);
      return;
    }

    setStage("Verbinden met EasyVoras database...");
    setProgress(10);

    // API call
    const response = await fetch('/api/sql-ingest/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        batch_name: seriesName,
        volgnummer_list: volgnummers
      })
    });

    setProgress(90);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Generatie mislukt');
    }

    const data = await response.json();
    
    setProgress(100);
    setCompleted(true);
    setGeneratedCount(data.proposals_generated);
    
    toast({
      title: "Voorstellen gegenereerd",
      description: `${data.proposals_generated} voorstellen uit ${data.articles_processed} artikelen.`
    });
    
    // Redirect naar batch
    setTimeout(() => {
      router.push(`/proposals?batchId=${data.batch_id}`);
    }, 1500);
    
  } catch (error) {
    toast({
      title: "Error bij genereren",
      description: error.message,
      variant: "destructive"
    });
  } finally {
    setGenerating(false);
  }
};
```

**UI Update: Tekstinvoer**

```tsx
<div className="space-y-2">
  <Label htmlFor="article-codes">Artikelnummers</Label>
  <Textarea
    id="article-codes"
    value={articleCodes}
    onChange={(e) => setArticleCodes(e.target.value)}
    placeholder="Voer artikelnummers in (één per regel)
423854
424783
56012
425137"
    rows={10}
    disabled={generating}
    className="font-mono"
  />
  <p className="text-xs text-muted-foreground">
    Voer één artikelnummer per regel in. Alleen cijfers.
  </p>
</div>
```

---

## 9) Security & Deployment

### 9.1 Intern Netwerk (Huidig)

**Setup:**
- Directe SSH + MySQL connectie OK
- Read-only MySQL user aanmaken
- Credentials in `.env`

**Read-only User Script:**
```sql
-- Op EasyVoras Linux server
CREATE USER 'drt_readonly'@'%' IDENTIFIED BY 'STRONG_PASSWORD';
GRANT SELECT ON evmwin.evlgfil TO 'drt_readonly'@'%';
GRANT SELECT ON evmwin.efiliaal TO 'drt_readonly'@'%';
GRANT SELECT ON evmwin.eplu TO 'drt_readonly'@'%';
FLUSH PRIVILEGES;
```

**.env Configuratie:**
```env
# EasyVorasWindows SQL Connection
EVORAS_SSH_HOST=192.168.0.101
EVORAS_SSH_USER=admin
EVORAS_SSH_PASSWORD=xxx
EVORAS_SSH_KEY_PATH=  # optioneel
EVORAS_MYSQL_HOST=localhost
EVORAS_MYSQL_PORT=3306
EVORAS_MYSQL_USER=drt_readonly
EVORAS_MYSQL_PASSWORD=xxx
EVORAS_MYSQL_DATABASE=evmwin
```

### 9.2 Internet Deployment (Toekomst)

**Aanbevolen Architectuur:**

```
[DRT Web App (Internet)]
    ↓ (VPN required)
[API Gateway/Proxy

]
    ↓ (Rate limiting, IP whitelist)
[SSH Tunnel]
    ↓
[EasyVoras SQL]
```

**Security Maatregelen:**
- VPN vereiste voor externe toegang
- API key authentication
- Query sanitization & prepared statements
- Connection pooling met timeouts
- Monitoring van abnormaal query gedrag
- Audit logging van alle SQL queries
- IP whitelist voor toegestane clients

---

## 10) Testing Strategie

### 10.1 Unit Tests

**Test maatbalk mappings:**
```python
def test_maatbalk_mapping_retrieval():
    # Test bekende maatbalk
    mapping = get_maatbalk_mapping(20, db)
    assert not mapping['error']
    assert mapping['positions'][0] == '32'
    assert mapping['positions'][8] == '48'
    
    # Test onbekende maatbalk
    mapping = get_maatbalk_mapping(999, db)
    assert mapping['error']
    assert 'ONBEKENDE MAATBALK' in mapping['message']
```

**Test SQL transformer:**
```python
def test_sql_row_transformation():
    sql_row = {
        'VOLGNUMMER': '423423',
        'FILIAALNUMMER': 31,
        'FILIAALNAAM': 'Tilburg',
        'MAATBALK_ID': 20,
        'VOORRAAD1': 2, 'VOORRAAD2': 1, 'VOORRAAD3': 0, ...
        'VERKAANT1': 5, 'VERKAANT2': 3, ...
    }
    
    mapping = get_maatbalk_mapping(20, db)
    records = transform_sql_row_to_voorraad_records(sql_row, 1, mapping, db)
    
    assert len(records) > 0
    assert records[0].source == 'sql'
    assert records[0].maat in ['32', '34', '36', ...]
```

### 10.2 Integration Tests

**Test complete SQL flow:**
```python
def test_sql_ingest_end_to_end():
    # 1. Generate batch from SQL
    response = client.post('/api/sql-ingest/generate', json={
        'batch_name': 'Test Batch',
        'volgnummer_list': ['423423', '54448']
    })
    
    assert response.status_code == 200
    data = response.json()
    batch_id = data['batch_id']
    
    # 2. Verify ArtikelVoorraad records created
    records = db.query(ArtikelVoorraad).filter_by(batch_id=batch_id).all()
    assert len(records) > 0
    assert all(r.source == 'sql' for r in records)
    
    # 3. Verify proposals generated
    proposals = db.query(Proposal).filter_by(pdf_batch_id=batch_id).all()
    assert len(proposals) > 0
```

### 10.3 Validation Tests

**Vergelijk SQL vs PDF output:**
```python
def test_sql_vs_pdf_comparison():
    # Upload PDF van artikel 423423
    pdf_batch_id = upload_pdf_and_get_batch_id('423423.pdf')
    
    # Generate SQL voor artikel 423423
    sql_batch_id = generate_sql_batch(['423423'])
    
    # Vergelijk ArtikelVoorraad records
    pdf_records = get_voorraad_records(pdf_batch_id, '423423')
    sql_records = get_voorraad_records(sql_batch_id, '423423')
    
    # Vergelijk voorraad per maat per filiaal
    for pdf_rec, sql_rec in zip(pdf_records, sql_records):
        assert pdf_rec.maat == sql_rec.maat
        assert pdf_rec.voorraad == sql_rec.voorraad
        assert pdf_rec.verkocht == sql_rec.verkocht
```

---

## 11) Implementation Roadmap

### Fase 1: Foundation (Week 1-2)

**Doel:** Basis infrastructuur opzetten

- [ ] Create `maatbalk_mappings` tabel
- [ ] Seed initiele maatbalk data (1, 2, 7, 9, 10, 20, 21)
- [ ] Migrate `ArtikelVoorraad` (+source, +maatbalk_id)
- [ ] Setup read-only SQL user op EasyVoras
- [ ] Test SSH + MySQL connectie manueel

### Fase 2: Backend Core (Week 3-4)

**Doel:** SQL extractor en transformer werkend krijgen

- [ ] Implementeer `EvorasConnector` class
- [ ] Implementeer `SQLDataTransformer` class
- [ ] Test met enkele bekende artikelen (423423, 54448)
- [ ] Verificatie: ArtikelVoorraad records matchen PDF output
- [ ] Unit tests voor transformer

### Fase 3: API Integration (Week 5)

**Doel:** SQL ingest endpoint werkend

- [ ] Implementeer `/api/sql-ingest/generate` endpoint
- [ ] Error handling voor onbekende maatbalken
- [ ] Logging en monitoring
- [ ] Integration tests
- [ ] Performance testing (batch van 50 artikelen)

### Fase 4: Frontend (Week 6)

**Doel:** UI voor SQL generation

- [ ] Update `generate-proposals.tsx` met echte API call
- [ ] Tekstinvoer voor artikelnummers
- [ ] Progress tracking (real-time)
- [ ] Error weergave (onbekende maatbalken, etc)
- [ ] "Bron" kolom in reekslijst

### Fase 5: Maatbalk Learning (Week 7)

**Doel:** PDF uploads trainen nieuwe maatbalken

- [ ] Extract maat labels uit PDF header
- [ ] Auto-create maatbalk mappings bij nieuwe IDs
- [ ] UI waarschuwing bij onbekende maatbalk + upload optie
- [ ] Validatie van nieuwe mappings

### Fase 6: Testing & Validation (Week 8)

**Doel:** Volledige validatie en bugfixes

- [ ] Test 20+ artikelen SQL vs PDF vergelijking
- [ ] Edge cases (missing maatbalk, lege voorraad, etc)
- [ ] Performance optimalisatie
- [ ] Security audit
- [ ] Documentatie voltooien

### Fase 7: Deployment (Week 9)

**Doel:** Live gang op intern netwerk

- [ ] Deploy naar productie omgeving
- [ ] Monitor eerste SQL generations
- [ ] User training
- [ ] Feedback verzamelen
- [ ] Itereren op basis van feedback

---

## 12) Belangrijke Beslissingen Samenvatting

| Beslissing | Rationale |
|-----------|-----------|
| **Parallel systems (PDF + SQL)** | Beide blijven beschikbaar voor flexibiliteit |
| **Dezelfde ArtikelVoorraad structuur** | Algoritme blijft ongewijzigd, minimale impact |
| **Maatbalk learning via PDF** | Automatisch nieuwe maatbalken "trainen" |
| **Error bij onbekende maatbalk** | Gebruiker moet eerst PDF uploaden |
| **Source kolom in UI** | Transparantie over databron |
| **Read-only SQL user** | Security best practice |
| **Tekstinvoer artikelnummers** | Eenvoudig kopiëren uit Excel/tekst |

---

## 13) Open Vragen / Te Beslissen

- [ ] **Maatbalk fallback:** Wat als `eplu` leeg blijft? Alternatieve tabel? Config file?
- [ ] **Batch size limit:** Max artikelen per SQL generatie? (perf vs usabilty)
- [ ] **Caching:** Cache SQL queries voor herhaalde artikelen?
- [ ] **Sync frequency:** Hoe vaak sync tussen EasyVoras en DRT?
- [ ] **Top 40 integratie:** Automatische artikelselectie in v2.1?

---

**Document Status:** Compleet en klaar voor implementatie  
**Laatste Update:** 2025-11-07 00:22 (Europe/Amsterdam)  
**Versie:** 2.0 (SQL Generation Specification)
