# Browser Debugging

Deze setup geeft DRT een vaste troubleshooting-browser waar consolefouten, page errors en mislukte requests live uitgelezen kunnen worden.

## Wat dit oplost

- Je hoeft niet meer alleen op screenshots of handmatige DevTools-copy/paste te vertrouwen.
- De browser draait met remote debugging aan.
- Een watcher kan live console- en netwerkfouten loggen naar terminal en bestand.
- Playwright smoke tests geven een snelle sanity check voor frontend en backend.

## Nieuwe commando's

Vanuit de project root:

```powershell
npm run browser:debug
npm run browser:watch
npm run browser:smoke
```

`browser:watch` probeert eerst te verbinden met een browser op remote debug port `9222`. Als dat niet lukt, start het script automatisch zelf een headed Playwright Chromium-venster met DevTools open.

## Aanbevolen workflow

1. Start de app:

```powershell
.\dev.ps1
```

2. Start de debugbrowser:

```powershell
npm run browser:debug
```

3. Start de watcher in een aparte terminal:

```powershell
npm run browser:watch
```

Als de externe debugbrowser niet bereikbaar is, opent de watcher zelf een bruikbare debugbrowser.

4. Reproduceer het probleem in de debugbrowser.

5. Lees live output in de terminal of open het logbestand in `browser-artifacts/`.

## Wat de watcher logt

- `CONSOLE`: console.log, warn, error
- `PAGEERROR`: uncaught runtime exceptions
- `REQUESTFAILED`: netwerkrequests die falen
- `RESPONSE`: HTTP responses met status 400+
- `NAVIGATED`: hoofd-navigaties per pagina

## Belangrijke paden

- Browserprofiel: `C:\Codex\DRT\.browser-debug-profile`
- Watcher-logs: `C:\Codex\DRT\browser-artifacts`
- Frontend runtime logs: `C:\Codex\DRT\logs\frontend.out.log`
- Backend runtime logs: `C:\Codex\DRT\logs\backend.out.log`

## Opmerkingen

- De debugbrowser gebruikt een apart profiel zodat gewone persoonlijke browser-sessies niet worden geraakt.
- Als je met bestaande sessies wilt blijven werken, gebruik dan steeds dezelfde debugbrowser en profielmap.
- Voor reproduceerbare regressiechecks is `npm run browser:smoke` de snelste eerste stap.
