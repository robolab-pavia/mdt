# Fondamenti di Informatica 30/11/2020

## Istruzioni e raccomandazioni

* Assegnare il nome del file in base al proprio cognome, chiamandolo `proprio_cognome.c` (es. `facchinetti.c`); basta aprirlo con `micro proprio_cognome.c`.
* Salvare periodicamente il proprio programma nella directory di lavoro.
* Il primo commento del programma deve riportare **nome**, **cognome** e **numero di matricola**.
* Vengono valutati positivamente aspetti quali la leggibilità del programma, l'uso appropriato dei commenti e del nome di variabili e funzioni, modularità e generalità del codice.
* È possibile far uso di manuali, testi, appunti e dispense, ma non di eserciziari (raccolte di esercizi risolti).

ATTENZIONE: Rispettare rigorosamente il formato di stampa dei risultati specificato per ciascuna richiesta.

# Contesto

Un file contiene le password utilizzate dagli utenti di un servizio web.
Le password sono memorizzate una per riga.
Una password ha lunghezza massima pari a $20$ caratteri.

Un esempio di file con tale formato, che contiene $3$ password, è il seguente:

    123456
    qwerty
    i*,adsl923

Il numero di righe nel file non è noto.

# Informazioni sul programma richiesto

Si scriva un programma in linguaggio C in grado di elaborare un file avente il formato descritto, al fine di restituire i risultati indicati nei punti specificati di seguito.
Il programma deve poter essere invocato da linea di comando.
Un esempio di invocazione è la seguente:

    ./a.out nome_input_file

dove **a.out** è il nome del programma eseguibile da invocare; **nome_input_file** è il nome del file di dati da elaborare.


**IMPORTANTE**: il programma finale dovrà produrre la stampa di risultati esattamente col formato specificato nei vari punti.
In particolare, _non aggiungere all'output del testo non richiesto_.

Eventuali righe di output aggiuntive che si vogliono generare in fase di debug, ma che si vogliono escludere dai test, possono essere stampate includendo in prima posizione il carattere #. 

Il buon funzionamento del programma può essere verificato col comando

    pvcheck ./a.out

dove **a.out** è il nome del file eseguibile.

# RICHIESTE

## 1. Lunghezza minima

Valutare la lunghezza di tutte le password, individuando la lunghezza minima (`MIN`) e quella massima (`MAX`).

Una password valida deve essere lunga minimo 8 caratteri.
Verificare quali password **non rispettano** il requisito di lunghezza minima.
Conteggiare il numero di password che non risultano valide in accordo al criterio indicato.

Detto `C` il numero di password non valide, stampare tutti i valori calcolati con il seguente formato:

    [LUNGHEZZE]
    MIN
    MAX
    C

## 2. Presenza di almeno due caratteri numerici

Una password valida deve contenere almeno 2 caratteri numerici.
Individuare le password che **non rispettano** questo requisito.
Stampare tutte le password che non risultano valide, nello stesso ordine col quale compaiono nel file di input, e col seguente formato:

    [NUMERICI]
    pass1
    pass2
    ...

Se non ci sono password da stampare, si stampi la stringa `"/NULLA/"` (senza i doppi apici) al posto dell'elenco delle password.

SUGGERIMENTO: si può utilizzare la funzione `isdigit` per determinare se un carattere corrisponde ad una cifra numerica (cifre tra 0 e 9).
La funzione, utilizzabile per esempio con `isdigit(car)` accetta in ingresso il carattere `car` da valutare, e restituisce un valore non nullo (quindi vero) in caso il carattere sia numerico, oppure 0 in caso contrario.
Questa funzione si può utilizzare includendo il file di intestazione `ctype.h`.

## 3. Caratteri speciali

Determinare il numero di password che *non contengono* nemmeno un carattere speciale.
I caratteri speciali sono tutti i caratteri diversi da quelli alfanumerici (che sono, a loro volta, i caratteri alfabetici maiuscoli e minuscoli, e quelli numerici).
Indicato con `M` tale valore, stamparlo con il seguente formato:

    [SPECIALI]
    M

SUGGERIMENTO: si può utilizzare la funzione `isalnum` per determinare se un carattere è alfanumerico.
La funzione, utilizzabile per esempio con `isalnum(car)`, accetta in ingresso il carattere `car` da valutare, e restituisce un valore non nullo (quindi vero) in caso il carattere sia alfanumerico, oppure 0 in caso contrario.
Questa funzione si può utilizzare includendo il file di intestazione `ctype.h`.

## 4. Password non ripetute

Nel file possono essere presenti delle password ripetute **due o più volte**.
Stampare le password che compaiono nel file **una sola volta**.

Si stampino le password con il seguente formato:

    [NON-RIPETUTE]
    pass1
    pass2
    ...

Se non è presente nemmeno una password che non sia ripetuta, ovvero ogni password ha almeno un duplicato, si stampi la stringa `"/NULLA/"` (senza i doppi apici) al posto dell'elenco delle password.

## 5. Ordinamento

Ordinare le righe lette dal file in senso crescente.
Stampare le prime 20 righe dell'elenco ordinato, oppure tutte le righe se sono meno di 20.
Utilizzare la funzione `strcmp` per determinare l'ordinamento in presenza di caratteri non alfabetici.

Stampare le righe ordinate col seguente formato (esempio):

    [ORDINAMENTO]
    123456
    i*,adsl923
    qwerty

