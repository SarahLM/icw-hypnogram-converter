# icw-hypnogram-converter

Zur Ausführung des Programms muss zunächst das Modul EdfReader installiert werden über: 

**"pip3 install --user edfrd"**

Eventuell muss vorher noch der Paketmanager installiert werden, was abhängig vom Betriebssystem ist. 

**"sudo apt-get install python3-pip"**

Die Hilfe zur Programmnutzung lässt sich mit **"--help"** aufrufen.

Zum Starten des aktuellen Programms, ist es notwendig die Datei converter.py zu starten.
Hierbei werden zwei Parameter übergeben. 

Dateiname z.B. cmpstudy.xml und Zieldatei.json

**"python3 converter.py [Dateiname] *optional*[neuer Dateiname]"**

Wird kein Name für die Zieldatei angegeben, wird default der Dateiname der Ursprungsdatei inklusive der ursprünglichen Dateiendung verwendet.

Auf der Konsole wird ausgegeben, ob die konvertierung erfolgreich war und eine json im Ordner "Ausgabedateien" gespeichert. 

Aktuell werden 4 verschiedene Dateien konvertiert, eine edf, zwei xml und eine txt.
