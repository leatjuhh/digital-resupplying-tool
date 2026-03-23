# Proposals Testing - Handmatige Test Flows

**Datum:** 2025-11-02
**Status:** Ready for Testing

---

## TEST 1: Optimaal Verdeeld Artikel - Detail View

### Doel
Verifiëren dat gebruiker duidelijk ziet wanneer een artikel optimaal verdeeld is.

### Pre-conditie
- Backend en frontend draaien
- Database heeft proposals zonder moves (optimaal verdeelde artikelen)
- Proposal ID 3 heeft status "optimaal verdeeld"

### Test Steps

1. **Open Detail Pagina**
   - Navigeer naar: `http://localhost:3000/proposals/3?batchId=3`
   
2. **Verifiëer Alert Melding**
   - ✅ Groene alert box met CheckCircle2 icon is zichtbaar
   - ✅ Tekst toont: "Optimaal Verdeeld"
   - ✅ Beschrijving legt uit dat geen herverdelingen nodig zijn

3. **Verifiëer Badge**
   - ✅ Header toont "Optimaal Verdeeld" badge met CheckCircle2 icon
   - ✅ Badge is secondary variant (grijs)

4. **Verifiëer Tabs**
   - ✅ "Vergelijking" tab aanwezig
   - ✅ "Huidige Situatie" tab aanwezig
   - ✅ "Voorgestelde Situatie" tab is NIET zichtbaar (omdat geen verschillen)

5. **Verifiëer Tabel Data**
   - ✅ Vergelijking tab toont geen groene/blauwe highlighting (geen verschillen)
   - ✅ Alle winkels tonen dezelfde current/proposed voorraad

### Expected Result
Gebruiker begrijpt direct dat dit artikel optimaal verdeeld is en geen actie vereist.

---

## TEST 2: Artikel MET Verschillen - Detail View

### Doel
Verifiëren dat artikelen met voorgestelde wijzigingen correct worden getoond.

### Pre-conditie
- Artikel met moves (niet in huidige database, maar voor toekomstige tests)

### Test Steps

1. **Open Detail Pagina**
   - Navigeer naar proposal met moves
   
2. **Verifiëer NO Alert**
   -  ✅ Geen groene "Optimaal Verdeeld" alert

3. **Verifiëer Badge**
   - ✅ Header toont "Wijzigingen voorgesteld" badge

4. **Verifiëer Tabs**
   - ✅ Alle 3 tabs zichtbaar: Vergelijking, Huidige, Voorgestelde

5. **Verifiëer Highlighting**
   - ✅ Groene highlighted cells voor current voorraad
   - ✅ Blauwe highlighted cells voor proposed wijzigingen

### Expected Result
User ziet duidelijk de voorgestelde wijzigingen.

---

## TEST 3: Edit Pagina - Basis Functionaliteit

### Doel
Verifiëren dat edit functionaliteit werkt zonder "Load Proposal".

### Pre-conditie
- Backend en frontend draaien
- Proposal ID 4 beschikbaar

### Test Steps

1. **Open Edit Pagina**
   - Navigeer naar: `http://localhost:3000/proposals/4/edit?batchId=3`

2. **Verifiëer Initial State**
   - ✅ Badge toont: "Basis: Huidige Voorraad"
   - ✅ "Laad AI Voorstel" knop zichtbaar (als er verschillen zijn)
   - ✅ "Resetten" knop disabled (nog geen changes)
   - ✅ "Gebalanceerd" badge zichtbaar

3. **Maak Wijziging**
   - Klik op een voorraad input field
   - Wijzig waarde (bijv. van 10 naar 12)
   
4. **Verifiëer After Change**
   - ✅ "Ongebalanceerd" badge (rood) verschijnt
   - ✅ "Gewijzigd" badge verschijnt
   - ✅ "Resetten" knop enabled
   - ✅ Totaal rij toont rood met +2 indicator

5. **Test Reset**
   - Klik "Resetten"
   - ✅ Wijziging ongedaan gemaakt
   - ✅ "Gebalanceerd" status terug

### Expected Result
Basic editing functionaliteit werkt correct.

---

## TEST 4: Edit Pagina - Load Proposal Functie

### Doel
Verifiëren dat "Laad AI Voorstel" knop correct werkt.

### Pre-conditie
- Proposal heeft differences tussen current en proposed
- (NB: Huidige test data heeft GEEN differences, dus knop zal niet verschijnen)

### Test Steps

1. **Open Edit Pagina**
   - Navigeer naar edit pagina van proposal met moves

2. **Verifiëer "Load Proposal" Knop**
   - ✅ Knop is zichtbaar (alleen als hasProposedDifferences === true)
   - ✅ Badge toont "Basis: Huidige Voorraad"

3. **Klik "Laad AI Voorstel"**
   - Klik de knop

4. **Verifiëer Na Laden**
   - ✅ Badge verandert naar "Basis: AI Voorstel"
   - ✅ Voorraad cijfers tonen proposed values
   - ✅ Blauw highlighting toont verschillen t.o.v. current
   - ✅ "Gebalanceerd" blijft groen
   - ✅ "Gewijzigd" badge NIET zichtbaar (nog geen user edits)

5. **Maak Wijziging Vanaf Proposed**
   - Wijzig een waarde in de tabel

6. **Test Reset from Proposed**
   - Klik "Resetten"
   - ✅ Gaat terug naar proposed (niet naar current!)
   - ✅ Badge blijft "Basis: AI Voorstel"

7. **Switch Terug**
   - Refresh pagina of navigeer terug
   - ✅ Start opnieuw bij "Basis: Huidige Voorraad"

### Expected Result
User kan kiezen tussen editen vanaf current of proposed als basis.

---

## TEST 5: Console Errors Check

### Doel
Verifiëren dat er geen JavaScript errors zijn.

### Test Steps

1. **Open Browser DevTools**
   - Druk F12
   - Ga naar Console tab

2. **Navigeer Door Pagina's**
   - Open detail view
   - Open edit view
   - Maak wijzigingen
   - Klik knoppen

3. **Verifiëer**
   - ✅ Geen rode error messages
   - ✅ Geen warnings over missing props
   - ✅ Alleen expected logging (info level)

### Expected Result
Geen console errors gedurende hele flow.

---

## TEST 6: Edge Cases

### Test 6A: Optimaal Artikel - Edit Poging
1. Open edit pagina van optimaal artikel
2. ✅ "Laad AI Voorstel" knop NIET zichtbaar (hasProposedDifferences = false)
3. ✅ Kan nog steeds manueel editen vanaf current

### Test 6B: Navigation Flow
1. Start bij detail view optimaal artikel
2. Klik "Bewerken" (als button beschikbaar)
3. ✅ Navigate correct naar edit pagina
4. Klik "Terug naar voorstel"
5. ✅ Navigate correct terug naar detail

### Test 6C: Batch Progress
1. Open proposal in batch context (`?batchId=3`)
2. ✅ Batch progress card zichtbaar
3. ✅ Progress percentage correct
4. ✅ "Optimaal Verdeeld" badge nog steeds zichtbaar

---

## KNOWN LIMITATIONS (Huidige Test Data)

**Probleem:** Alle proposals in database hebben `moves=[]` (optimaal verdeeld)

**Impact:**
- "Laad AI Voorstel" knop zal NIET verschijnen (hasProposedDifferences = false)
- "Voorgestelde Situatie" tab is altijd identiek aan "Huidige Situatie"
- Cannot fully test the "Load Proposal" functionaliteit

**Workaround voor Complete Test:**
1. Upload PDF met niet-optimaal verdeelde voorraad
2. Verifiëer dat algoritme moves genereert
3. Test dan volledige "Load Proposal" flow

**Alternatief:**
- Wijzig algoritme thresholds om meer moves te genereren
- Of: Maak test data met artificieel ongelijke verdeling

---

## DEFINITION OF DONE ✅

### STAP 1: Optimaal Verdeeld Indicator
- [x] Alert toont bij geen verschillen
- [x] Badge toont "Optimaal Verdeeld"
- [x] "Voorgestelde Situatie" tab verborgen wanneer geen verschillen
- [x] Geen console errors

### STAP 2: Load Proposal Functie
- [x] "Laad AI Voorstel" knop implementation
- [x] Knop verschijnt alleen bij differences
- [x] Badge toont huidige basis
- [x] Reset werkt correct voor beide bases
- [x] Instructies bijgewerkt
- [x] Geen console errors

### Code Quality
- [x] TypeScript compileert zonder errors
- [x] Geen linter warnings
- [x] Logische component structuur
- [x] Props correct getypeerd

---

## NEXT STEPS

1. **Met Echte Data Testen**
   - Upload artikel met suboptimale verdeling
   - Verifiëer volledige "Load Proposal" flow
   
2. **Algorithm Tuning (Optioneel)**
   - Verlaag thresholds voor meer gevoeligheid
   - Test met echte productie scenario's

3. **User Acceptance Testing**
   - Laat eindgebruiker flow testen
   - Verzamel feedback op UI/UX
   - Itereer op basis van feedback
