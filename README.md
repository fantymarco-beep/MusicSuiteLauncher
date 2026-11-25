# Music Suite Launcher

Launcher desktop in stile minimalista **ArtCraft** per avviare, monitorare e consultare i software e le raccolte musicali locali su `E:\`, senza modificare né spostare le cartelle esistenti.

## Caratteristiche
* Griglia a schede in stile chiaro/minimalista con barra di ricerca, filtri per categoria (`Software`, `Catalogo`, `Raccolta`, `Attivi`) e ordinamento.
* **Icone dinamiche:** in scala di grigi a riposo, si colorano al passaggio del mouse e restano accese a colori mentre il software è in esecuzione.
* **Istruzioni integrate:** pulsante dedicato su ogni scheda per leggere `ISTRUZIONI.md` / `README.md` direttamente in una finestra modale.
* **Accesso rapido:** apertura diretta della cartella su `E:\` e collegamento al repository GitHub.

## Avvio
Esegui `Avvia_Music_Suite.bat` oppure:
```powershell
python main.py
```

## Dipendenze
* `pywebview`
* `fastapi`
* `uvicorn`
* `psutil`
* `markdown`
