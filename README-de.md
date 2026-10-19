[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/fmainz/ha-ipfire?include_prereleases=&sort=semver&color=blue)](https://github.com/fmainz/ha-ipfire/releases/)
![last commit](https://img.shields.io/github/last-commit/fmainz/ha-ipfire)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Paket-Downloads](https://img.shields.io/github/downloads/fmainz/HA-IPFire/total?style=flat-square&color=red&label=Paket-Downloads)
[![stars](https://img.shields.io/github/stars/fmainz/HA-IPFire)](https://github.com/FMainz/HA-IPFire/stargazers)

# HA-IPFire

## 🇩🇪 Deutsch

Home-Assistant-Integration zur Überwachung von IPFire-Systeminformationen, Netzwerkstatus, Traffic-Statistiken und zur Steuerung der Internetverbindung.

Diese Dokumentation ist auch in 🇬🇧 [englischer Sprache](README.md) verfügbar.

## Inhaltsverzeichnis

- [Neues in dieser Version](#neues-in-dieser-version)
- [Funktionen](#funktionen)
- [IPFire](#ipfire)
- [IPFire API](#ipfire-api)
  - [Installation des IPFire-CGI](#installation-des-ipfire-cgi)
- [Sensoren](#sensoren)
- [Steuerung der Internetverbindung](#steuerung-der-internetverbindung)
- [Abfrageintervall](#abfrageintervall)
- [SSL-Zertifikate](#ssl-zertifikate)
- [Authentifizierung](#authentifizierung)
- [Installation](#installation)
  - [HACS](#hacs)
  - [Manuelle Installation](#manuelle-installation)
- [Konfiguration](#konfiguration)
- [IPFire-Daten](#ipfire-daten)
- [Gerät](#gerät)
- [Verbindungssteuerung](#verbindungssteuerung)
- [Home Assistant](#home-assistant)
- [Support](#support)
- [Repository](#repository)
- [Lizenz](#lizenz)

---

## Neues in dieser Version

### v0.3.5

* Die Entwicklung des IPFire-CGI `api.cgi` wird im eigenständigen Repository [IPFire-API](https://github.com/FMainz/IPFire-API) fortgeführt.

### v0.3.4

* Die HACS-ZIP-Veröffentlichung vorbereitet und die Anzeige der GitHub-Paketdownloads angepasst.

### v0.3.3

* Systeminformationssensoren für IPFire-Version, Pakfire-Version, Kernel-Version, Architektur, CPU-Modell, CPU-Anzahl, Modell und Hersteller hinzugefügt.
* Sensoren für CPU-Auslastung, CPU-Gesamtzeit und CPU-Leerlaufzeit hinzugefügt.
* Arbeitsspeichersensoren für Gesamt, verfügbar, frei, Puffer und Cache hinzugefügt.
* Sensoren für Festplattenspeicher (gesamt, belegt, verfügbar und Auslastung) hinzugefügt.
* Sensoren für Festplattentemperatur und SMART-Fehler hinzugefügt.
* Sensor für die IPFire-Betriebszeit hinzugefügt.
* Informationen zu verfügbaren Paket-Updates hinzugefügt.
* Verbesserte Icon-Verwaltung für Sensoren und Netzwerkschnittstellen hinzugefügt.
* Die Icons der Netzwerkschnittstellen zeigen nun dynamisch an, ob eine Schnittstelle verbunden oder getrennt ist.

## Funktionen

HA-IPFire bietet folgende Funktionen:

* Download-Trafficzähler
* Upload-Trafficzähler
* Aktuelle Download-Geschwindigkeit
* Aktuelle Upload-Geschwindigkeit
* Status der Internetverbindung
* Dauer der Internetverbindung
* Connect- und Disconnect-Steuerung
* Konfigurierbares Abfrageintervall
* Abfrageintervall von 5 bis 60 Sekunden
* Optionale SSL-Zertifikatsprüfung
* Authentifizierung mit Benutzername und Passwort
* HACS-kompatibel
* Deutsche und englische Übersetzungen

## IPFire

Die Integration ruft die Verkehrsinformationen über folgenden IPFire-Endpunkt ab:

```text
/cgi-bin/speed.cgi
```

Die Standard-URL lautet:

```text
https://ipfire.local:444
```

Der Hostname oder die IP-Adresse kann während der Einrichtung geändert werden.

HA-IPFire verwendet die von IPFire bereitgestellten kumulativen Trafficzähler, um daraus die aktuelle Übertragungsgeschwindigkeit zu berechnen.

## IPFire API

Das optionale CGI-Script `api.cgi` ergänzt `speed.cgi` um Systeminformationen und Steuerungsfunktionen. Es wird im eigenständigen Projekt [IPFire-API](https://github.com/FMainz/IPFire-API) weiterentwickelt.

Zusätzlich zum Verbindungsstatus und den Steuerungsaktionen liefert die API unter anderem Informationen zu:

* IPFire-, Pakfire- und Kernel-Version sowie Systemhersteller, -modell und Architektur
* CPU-Modell und Anzahl der Kerne
* Arbeitsspeicher und Festplattenbelegung einschließlich I/O-Statistiken und SMART-Status
* Status der Netzwerkschnittstellen und IPFire-Dienste
* installierten Add-ons und deren Status
* verfügbaren Core- und Paket-Updates

Eine vollständige Beschreibung der JSON-Felder findest du in der [IPFire-API-Dokumentation](https://github.com/FMainz/IPFire-API/blob/main/README-de.md#endpunkt).

### Verbindungssteuerung

Das Script `api.cgi` ermöglicht es HA-IPFire, die IPFire-Internetverbindung direkt aus Home Assistant zu steuern.

Folgende Aktionen stehen zur Verfügung:

* **Verbinden** – stellt die Internetverbindung her.
* **Trennen** – trennt die Internetverbindung.

Wenn **Verbinden** bei bereits bestehender Verbindung betätigt wird, wird die aktuelle Verbindung getrennt und anschließend neu aufgebaut.

Die Verbindungssteuerung verwendet die native IPFire-Verbindungssteuerung, die durch das Script `api.cgi` bereitgestellt wird.

### Installation des IPFire-CGI

Die aktuelle Version von `api.cgi` und die ausführliche Dokumentation findest du im [eigenständigen IPFire-API-Projekt](https://github.com/FMainz/IPFire-API). Installiere das CGI-Script manuell auf der IPFire-Firewall. HACS installiert die Home-Assistant-Integration; die Datei `api.cgi` muss zusätzlich auf IPFire eingerichtet werden.

Kopiere das CGI nach:

```text
/srv/web/ipfire/cgi-bin/api.cgi
```

Setze anschließend die korrekten Eigentümer und Berechtigungen:

```bash
chown root:root /srv/web/ipfire/cgi-bin/api.cgi
chmod 755 /srv/web/ipfire/cgi-bin/api.cgi
```

Das CGI verwendet die bestehende Authentifizierung der IPFire-Weboberfläche. Es sind keine zusätzlichen CGI-Zugangsdaten erforderlich.

**Sicherheit:** Das CGI sollte nur über die vertrauenswürdige IPFire-Weboberfläche erreichbar sein und nicht für nicht vertrauenswürdige Netzwerke zugänglich gemacht werden.

## Sensoren

Die Integration stellt folgende Sensoren bereit:

### Traffic

* **Download** – kumulativer Download-Traffic in Byte.
* **Upload** – kumulativer Upload-Traffic in Byte.
* **Download Speed** – aktuelle Download-Geschwindigkeit.
* **Upload Speed** – aktuelle Upload-Geschwindigkeit.

Die folgenden Sensoren und Funktionen erfordern, dass `api.cgi` auf der IPFire-Firewall [installiert](#installation-des-ipfire-cgi) ist.

### Internetverbindung

* **Connection Duration** – Dauer der aktuellen Internetverbindung.
* **Connection State** – aktueller Verbindungsstatus von IPFire.
* **Connected Since** – Zeitpunkt, zu dem die aktuelle Verbindung hergestellt wurde.
* **External IP** – aktuelle externe IP-Adresse.
* **External Hostname** – aktueller externer Hostname.

### System

* **IPFire Version**
* **Pakfire Version**
* **Kernel Version**
* **Architecture**
* **CPU Model**
* **CPU Count**
* **Model**
* **Vendor**
* **Uptime**
* **Package Updates**

### CPU

* **CPU Usage**
* **CPU Total**
* **CPU Idle**

### Arbeitsspeicher

* **Memory Total**
* **Memory Available**
* **Memory Free**
* **Memory Buffers**
* **Memory Cached**

### Festplatte

* **Disk Total**
* **Disk Used**
* **Disk Available**
* **Disk Usage**

### SMART

* **Disk Temperature**
* **SMART Errors**

## Steuerung der Internetverbindung

HA-IPFire stellt zwei Schaltflächen zur Steuerung der IPFire-Internetverbindung bereit:

* **Verbinden** – stellt die IPFire-Internetverbindung her.
* **Trennen** – trennt die IPFire-Internetverbindung.

Die Schaltflächen verwenden den dedizierten `api.cgi`-Endpunkt auf der IPFire-Firewall. Das CGI verwendet die native IPFire-Verbindungssteuerung und Authentifizierung.

> [!NOTE]
> Diese Funktion erfordert, dass `api.cgi` auf der IPFire-Firewall [installiert](#installation-des-ipfire-cgi) ist.

## Abfrageintervall

Das Abfrageintervall kann zwischen folgenden Werten eingestellt werden:

* **Minimum:** 5 Sekunden
* **Standard:** 30 Sekunden
* **Maximum:** 60 Sekunden

Das Intervall kann über den Schieberegler in 5-Sekunden-Schritten eingestellt werden.

Ein kürzeres Intervall liefert häufiger aktualisierte Daten, führt aber auch zu mehr Anfragen an die IPFire-Firewall.

## SSL-Zertifikate

Die SSL-Zertifikatsprüfung kann während der Konfiguration aktiviert oder deaktiviert werden.

Da IPFire-Installationen häufig selbst signierte Zertifikate verwenden, ist die Zertifikatsprüfung standardmäßig deaktiviert.

Wenn deine IPFire-Installation ein von einer vertrauenswürdigen Zertifizierungsstelle signiertes Zertifikat verwendet, kann die SSL-Prüfung aktiviert werden.

## Authentifizierung

Der IPFire-Endpunkt `speed.cgi` erfordert eine Authentifizierung.

HA-IPFire unterstützt daher:

* Benutzername
* Passwort

Die Zugangsdaten werden beim Hinzufügen der Integration zu Home Assistant konfiguriert.

## Installation

Direkt über diese Schaltfläche:

[![HA-IPFire in HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FMainz&repository=HA-IPFire&category=integration)

### HACS

HA-IPFire kann direkt über HACS installiert werden.

1.  **HACS** öffnen.
2.  **Integrationen** auswählen.
3.  Nach `HA-IPFire` suchen.
4.  Die Integration installieren.
5.  Home Assistant neu starten.

Wenn HA-IPFire in der normalen HACS-Suche nicht verfügbar ist, kann das Repository alternativ als benutzerdefiniertes Repository hinzugefügt werden:

```text
https://github.com/FMainz/HA-IPFire
```

Als Repository-Typ **Integration** auswählen.

Nach der Installation die Integration über:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

hinzufügen.

Nach:

**HA-IPFire**

suchen.

### Manuelle Installation

Folgendes Verzeichnis kopieren:

```text
custom_components/ipfire
```

nach:

```text
config/custom_components/ipfire
```

Home Assistant neu starten und IPFire über:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

hinzufügen.

## Konfiguration

Während der Einrichtung fragt HA-IPFire nach folgenden Informationen:

* **IPFire-URL** – Hostname oder IP-Adresse der IPFire-Firewall.
* **Benutzername** – Benutzername der IPFire-Weboberfläche.
* **Passwort** – das zugehörige IPFire-Passwort.
* **SSL-Zertifikatsprüfung** – aktiviert oder deaktiviert die Prüfung des SSL-Zertifikats.
* **Abfrageintervall** – legt fest, wie häufig HA-IPFire aktualisierte Daten von IPFire abruft.

Die Standard-IPFire-URL lautet:

```text
https://ipfire.local:444
```

HA-IPFire verwendet automatisch folgende Endpunkte:

```text
/cgi-bin/speed.cgi
```

für die Verkehrsdaten und

```text
/cgi-bin/api.cgi
```

für zusätzliche Systeminformationen, Netzwerk- und Dienststatus, Update-Informationen sowie die Steuerung der Internetverbindung.

Das Abfrageintervall kann zwischen **5 und 60 Sekunden** eingestellt werden.

## IPFire-Daten

Die Daten werden direkt aus IPFire ausgelesen. Für die Verkehrsstatistiken wird `speed.cgi` verwendet. Zusätzliche System-, Netzwerk-, Service- und Update-Informationen werden über die optionale `api.cgi` bereitgestellt.

## Gerät

HA-IPFire erstellt ein einzelnes Gerät für die IPFire-Firewall in Home Assistant.

Alle von der Integration bereitgestellten Sensoren und Bedienelemente werden diesem Gerät zugeordnet.

## Verbindungssteuerung

HA-IPFire kann die Internetverbindung der IPFire-Firewall direkt aus Home Assistant steuern.

Über die bereitgestellten Schaltflächen stehen folgende Aktionen zur Verfügung:

* **Verbinden** – stellt die Internetverbindung her.
* **Trennen** – trennt die Internetverbindung.

Wenn bei bestehender Verbindung **Verbinden** betätigt wird, wird die aktuelle Verbindung getrennt und anschließend neu aufgebaut.

## Home Assistant

HA-IPFire verwendet die nativen Sensor-Klassen, Einheiten und Statistikfunktionen von Home Assistant.

Die Trafficzähler werden als kumulative, kontinuierlich steigende Werte bereitgestellt und können dadurch von Home Assistant für Statistiken und den Verlauf verwendet werden.

Die aktuellen Übertragungsraten werden aus den Trafficzählern berechnet und als Datenraten bereitgestellt.

## Support

Wenn du einen Fehler findest oder einen Verbesserungsvorschlag hast, kannst du ein Issue im GitHub-Repository erstellen:

https://github.com/FMainz/HA-IPFire/issues

## Repository

https://github.com/FMainz/HA-IPFire

## Lizenz

HA-IPFire wird unter der MIT-Lizenz veröffentlicht.

---
