# Baseline Pipeline (historische tooling)

Deze map bevat de **historische pipeline** waarmee de eerste versie van het DRT-herverdelingsalgoritme gebouwd is op basis van handmatige herverdelingsdata. Deze logica is **niet** onderdeel van de DRT-runtime en wordt **niet** aangeroepen door de backend of frontend.

## Status

**Bevroren.** Deze tooling wordt niet actief doorontwikkeld. De actieve, live-runnende herverdelingslogica staat in `backend/redistribution/` binnen DRT en is verder doorontwikkeld sinds deze pipeline is bevroren.

## Waarom deze tooling nog bestaat

De pipeline heeft twee doelen die nog relevant kunnen zijn:

1. **Nieuwe weken verwerken** — wanneer er een nieuwe week manueel verwerkt wordt (Excel + PDFs), produceert deze pipeline de gestructureerde JSON-output die DRT in `backend/algorithm_data/` leest voor proposal-vergelijking en model-metrics.
2. **Baseline-vergelijking** — `run_baseline.py` genereert baseline-voorstellen per artikel die vergeleken kunnen worden met zowel manuele beslissingen als de huidige DRT-output.

Zodra DRT de manuele herverdelingsflow volledig heeft vervangen, kan deze map helemaal verdwijnen.

## Mapinhoud

| Bestand | Doel |
|---|---|
| `week_pipeline.py` | Hoofdpipeline: PDF + Excel → `week_XX/combined.json` |
| `week_sources.py` | Pad-resolutie en bronverwijzingen per week |
| `pipeline_config.py` | Actieve filialen, maten, uitgesloten stores |
| `dataset_refresh.py` | Orkestreert volledige refresh over alle weken |
| `training_data.py` | Bouwt trainingsvoorbeelden uit weekresultaten |
| `model_training.py` | Traint een sklearn-model op de trainingsdata |
| `extract_store_totals.py` | Haalt winkel-totalen uit een Excel-workbook |
| `run_baseline.py` | Entry point: genereer baseline-voorstellen voor één week |
| `run_pipeline.py` | Entry point: draai de week-pipeline voor één week |
| `run_week_update.py` | Entry point: verwerk één week of refresh alles |
| `run_training_data.py` | Entry point: genereer trainingsdata |
| `run_model_training.py` | Entry point: train het model |
| `legacy_redistribution/` | Bevroren kopie van het oude redistribution-pakket waar `baseline.py` op leunt. **Niet** verwarren met `backend/redistribution/` — dat is de actieve, nieuwere versie. |

## Vereisten om te draaien

- Python 3.13
- Extra packages boven de DRT-backend: `numpy`, `pandas`, `scikit-learn`, `openpyxl`, `pdfplumber`
- Excel-bronbestand en PDF-bronmap voor de week die je wilt verwerken (paden staan in `pipeline_config.py` en `week_sources.py`)

## Draaien

Vanuit de repo-root:

```powershell
cd tools\baseline-pipeline
..\..\backend\venv\Scripts\python.exe run_pipeline.py --year 2026 --week 17
```

`week_pipeline.py` voegt automatisch `backend/` toe aan `sys.path` zodat `pdf_extract` uit DRT gevonden wordt.

## Output

De pipeline schrijft standaard naar `../../backend/algorithm_data/{jaar}/week_{week}/` — dezelfde locatie die DRT inleest via `algorithm_import`.
