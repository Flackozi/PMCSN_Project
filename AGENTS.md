# AGENTS.md

## Scopo del file
Questo file fornisce contesto operativo a un coding agent per modificare il progetto in modo coerente con il caso di studio, con il codice esistente e con i vincoli metodologici dell'esame.

---

## Contesto del progetto
Questo progetto è sviluppato per l'esame di **Performance Modeling of Computer Systems and Networks**.

L'obiettivo del lavoro, come richiesto dalla traccia, è:
1. individuare un sistema oggetto di studio;
2. definire gli obiettivi dello studio;
3. costruire un **modello di simulazione** seguendo i passi degli algoritmi 1.1.1 e 1.1.2 del libro di Leemis & Park;
4. svolgere analisi del **transitorio**;
5. progettare opportunamente gli esperimenti;
6. mostrare i risultati sia in forma grafica sia numerica. fileciteturn0file2

Il libro di riferimento imposta lo sviluppo del modello in tre livelli principali:
- **modello concettuale**;
- **modello delle specifiche**;
- **modello computazionale**;
seguiti da **verifica**, **validazione**, **design degli esperimenti**, **analisi dei risultati** e documentazione. fileciteturn0file13

Il caso di studio adottato nel progetto riguarda il **workflow di una web application di e-commerce**, modellato come sequenza deterministica di visite ai nodi:
**A → B → A → P → A**. I tre nodi rappresentano:
- **A**: front-end / orchestrazione;
- **B**: core business logic;
- **P**: payment provider esterno. fileciteturn0file5

Gli obiettivi già presenti nella relazione di riferimento includono:
- sviluppo modello base
- valutazione impatto dell'introduzione del 2FA
- studio delle prestazioni del modello base con carico realistico (tasso di arrivo variabile e con distribuzione iper-esponenziale)
- implementazione modello migliorativo con scaling su server A e B
---

## Architettura logica del simulatore
Il progetto implementa una simulazione ad eventi discreti in Python.

### File principali
- `main.py`: punto di ingresso, menu di scelta e avvio delle simulazioni. fileciteturn0file12
- `simulator.py`: simulazione base finita e infinita. fileciteturn0file10
- `scaling_simulator.py`: logica di scaling e simulazione con carico variabile. fileciteturn0file11
- `sim_stats.py`: definizione delle strutture dati per stato, aree e statistiche. fileciteturn0file9
- `sim_utils.py`: utility per arrivi, servizi, batch, percentili e funzioni di supporto. fileciteturn0file8
- `sim_output.py`: scrittura CSV e generazione dei grafici. fileciteturn0file7
- `variables.py`: parametri globali di simulazione. fileciteturn0file6

### Stato del sistema
Il simulatore rappresenta i job che attraversano il workflow con classi logiche coerenti con la relazione:
- **Classe 1**: prima visita ad A e visita a B;
- **Classe 2**: seconda visita ad A e visita a P;
- **Classe 3**: terza visita ad A e uscita dal sistema. fileciteturn0file5

Nel codice:
- `A_jobs` contiene i job attualmente nel nodo A;
- `B_jobs` contiene i job nel nodo B;
- `P_jobs` contiene i job nel nodo P;
- le aree `area_A`, `area_B`, `area_P`, `area_A1`, `area_A2`, `area_A3` servono a calcolare metriche medie temporali. fileciteturn0file9turn0file10turn0file11

---

## Parametri attuali importanti
I parametri globali si trovano in `variables.py`. In particolare:
- `LAMBDA = 1.2` richieste/s;
- `STOP = 80000`;
- `REPLICATIONS = 10`;
- `K = 128`, `B = 4080` per la simulazione infinita/batch means;
- sono presenti parametri per carico variabile sinusoidale e spike, oltre a soglie di scaling (`RHO_UP`, `RHO_DOWN`, `MIN_SERVERS`, `MAX_SERVERS`, `SImax`). fileciteturn0file6

I tempi di servizio attualmente codificati in `sim_utils.py` sono:
- A1 = 0.2 s;
- A2 = 0.4 s;
- A3 = 0.1 s;
- B = 0.8 s;
- P = 0.4 s. fileciteturn0file8

Questi valori sono coerenti con lo scenario baseline descritto nella relazione di riferimento. fileciteturn0file5

---

## Regole operative per il coding agent
Quando modifichi il progetto, segui queste regole.

### 1. Non cambiare il significato del caso di studio
Le modifiche devono restare coerenti con il modello del workflow e-commerce A → B → A → P → A, salvo esplicita richiesta di introdurre un modello migliorativo o scenari alternativi. fileciteturn0file5

### 2. Mantieni la separazione tra livelli del progetto
Le modifiche devono rispettare questa distinzione concettuale:
- **concettuale**: descrizione del sistema e delle classi;
- **specifiche**: parametri, distribuzioni, routing, metriche;
- **computazionale**: implementazione Python. fileciteturn0file13

### 3. Non introdurre scorciatoie non motivate metodologicamente
Il progetto è un elaborato accademico di simulazione. Ogni modifica importante deve essere motivabile in termini di:
- obiettivo di studio;
- verifica/validazione;
- analisi del transitorio;
- simulazione finita o infinita;
- design degli esperimenti. fileciteturn0file2turn0file13

### 4. Preserva la compatibilità con l'output esistente
Se possibile, non rompere:
- intestazioni CSV già usate in `sim_output.py`;
- metriche già raccolte in `return_stats`;
- grafici di batch, transitorio e scaling. fileciteturn0file7turn0file10turn0file12

### 5. Preferisci modifiche minime e locali
Prima di riscrivere grandi porzioni di codice:
- individua il file corretto;
- verifica se la modifica può essere confinata lì;
- evita refactor strutturali se non strettamente necessari.

### 6. Mantieni coerenza con la semantica degli eventi
Nel progetto gli eventi principali sono:
- arrivo esterno in A;
- completamento in A;
- completamento in B;
- ritorno/completamento da P;
- eventi di scaling nel modello esteso. fileciteturn0file10turn0file11

Qualsiasi nuova funzionalità deve integrarsi in questo schema di simulazione ad eventi discreti.

---

## Priorità di intervento quando analizzi o modifichi il codice
Quando ti viene chiesto di fare una modifica, usa questo ordine.

### A. Capire se la modifica è metodologica o solo implementativa
Esempi:
- **metodologica**: introdurre warm-up, cambiare batch means, aggiungere intervalli di confidenza, aggiungere un nuovo scenario sperimentale;
- **implementativa**: correggere bug, rinominare campi, sistemare un grafico, aggiungere un CSV.

### B. Controllare prima `variables.py`
Molte richieste di modifica del comportamento dipendono da parametri globali. Prima di cambiare la logica, controlla se basta intervenire sui parametri. fileciteturn0file6

### C. Controllare poi `sim_utils.py`
Le distribuzioni di arrivo, i tempi di servizio e parte delle utility statistiche sono lì. Molte richieste su carico e servizio vanno implementate in questo file. fileciteturn0file8

### D. Toccare `simulator.py` e `scaling_simulator.py` solo se serve davvero
Questi file contengono la logica evento-per-evento. Le modifiche qui sono più delicate perché possono alterare direttamente la correttezza della simulazione. fileciteturn0file10turn0file11

---

## Controlli obbligatori dopo ogni modifica
Dopo una modifica al codice, il coding agent deve fare almeno questi controlli logici.

### Correttezza minima
- Il codice deve compilare/eseguire senza errori sintattici.
- I nomi importati devono essere coerenti con la struttura del progetto.
- Non devono essere introdotti riferimenti a funzioni inesistenti.

### Coerenza statistica
- Le metriche di attesa, risposta e utilizzazione non devono diventare negative senza motivo.
- Le aree integrate (`area_*`) devono restare finite.
- Le metriche devono restare coerenti con la semantica del nodo modellato.

### Coerenza sperimentale
- Le simulazioni finite devono continuare a produrre repliche.
- Le simulazioni infinite devono continuare a usare batching / batch means.
- I file CSV e i plot devono continuare a essere prodotti correttamente, se richiesti. fileciteturn0file10turn0file7

---

## Attenzione: punti delicati già presenti nel codice
Quando modifichi il progetto, fai particolare attenzione a questi punti.

### 1. Bug potenziale in `variables.py`
Nella funzione `set_simulation`, il ramo
```python
if type == 1:
    SIM_TYPE == FINITE
```
usa `==` invece di `=`. Questo sembra un bug, perché confronta invece di assegnare. Se viene richiesto di correggere i bug, questo è un punto da sistemare. fileciteturn0file6

### 2. Coerenza tra import e struttura reale del progetto
I file usano import come `utils.variables` e `simulation.simulator`, ma nella cartella disponibile i file risultano al livello principale. Prima di fare cambiamenti strutturali, verifica se nel repository reale esistono sottocartelle non incluse in questa copia o se serve riallineare gli import. fileciteturn0file12

### 4. Scaling
Nel modello di scaling, il carico variabile è guidato da `lambda_scaling(t)` e il numero di server di layer 1 viene adattato con `adjust_servers_layer1`. Prima di modificare la politica di scaling, verifica l'impatto su:
- completamenti in B;
- utilizzo dei server;
- serie temporali usate per i grafici. fileciteturn0file8turn0file11turn0file7

---

## Stile di modifica consigliato
Quando produci patch o nuove versioni di funzioni:
- mantieni i nomi esistenti se non c'è una ragione forte per cambiarli;
- aggiungi commenti solo dove chiariscono la logica di simulazione;
- evita di mescolare refactor estetici e correzioni funzionali nello stesso intervento;
- se una modifica impatta la relazione, segnala anche cosa andrebbe aggiornato nella documentazione.

---

## Come rispondere quando ti viene chiesto di modificare il codice
Quando lavori come coding agent su questo progetto:
1. identifica il file giusto;
2. spiega in una frase qual è il problema o l'obiettivo;
3. proponi la modifica più piccola possibile;
4. segnala eventuali effetti collaterali su metriche, output o relazione;
5. se tocchi la logica di simulazione, suggerisci anche come verificare la correttezza con un test rapido.

---

## Obiettivo finale del progetto
Ogni modifica deve aiutare a produrre un elaborato che sia:
- coerente con la traccia dell'esame;
- metodologicamente corretto;
- chiaro nella distinzione tra modello, simulazione, verifica, validazione e analisi sperimentale;
- utile per scrivere relazione e presentazione finale. fileciteturn0file2turn0file13turn0file0

