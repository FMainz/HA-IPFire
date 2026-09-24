[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/fmainz/ha-ipfire?include_prereleases=&sort=semver&color=blue)](https://github.com/fmainz/ha-ipfire/releases/)
![last commit](https://img.shields.io/github/last-commit/fmainz/ha-ipfire)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![GitHub total downloads](https://img.shields.io/github/downloads/fmainz/HA-IPFire/total?style=flat-square&color=red)
[![stars](https://img.shields.io/github/stars/fmainz/ha-ipfire)](https://github.com/FMainz/HA-IPFire/stargazers)

# HA-IPFire

🇬🇧 [English documentation](README.md)

## Inhaltsverzeichnis

- [Funktionen](#funktionen)
- [IPFire](#ipfire)
- [Sensoren](#sensoren)
- [Steuerung der Internetverbindung](#steuerung-der-internetverbindung)
  - [Installation des IPFire-CGI](#installation-des-ipfire-cgi)
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

## 🇩🇪 Deutsch

HA-IPFire ist eine Home-Assistant-Integration zur Überwachung von Netzwerkverkehrsstatistiken einer IPFire-Firewall.

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

Die Integration im Standard ruft die Verkehrsinformationen über folgenden IPFire-Endpunkt ab:

```text
/cgi-bin/speed.cgi
```

Die Standard-URL lautet:

```text
https://ipfire.local:444
```

Der Hostname oder die IP-Adresse kann während der Einrichtung geändert werden.

HA-IPFire verwendet die von IPFire bereitgestellten kumulativen Trafficzähler, um daraus die aktuelle Übertragungsgeschwindigkeit zu berechnen.

## Sensoren

Die Integration kann eine Vielzahl an Sensoren bereitstellen, zum Beispiel:

* **Download**
* **Upload**
* **Download Speed**
* **Upload Speed**
* **Connection Duration**
* **Connection State**

**Connection Duration** gibt die Dauer der aktuellen Internetverbindung in Sekunden an.

**Connection State** gibt den aktuellen Verbindungsstatus von IPFire an, beispielsweise `connected`, `connecting` oder `disconnected`.

Die kumulativen Trafficzähler werden in Byte bereitgestellt.

Die aktuellen Übertragungsraten werden aus der Differenz zwischen zwei aufeinanderfolgenden Messungen berechnet und intern in Byte pro Sekunde bereitgestellt.

Die Umrechnung der Einheiten und die Darstellung übernimmt Home Assistant.

## Steuerung der Internetverbindung

HA-IPFire stellt zwei Schaltflächen zur Steuerung der IPFire-Internetverbindung bereit:

* **Connect** startet die IPFire-Internetverbindung.
* **Disconnect** beendet die IPFire-Internetverbindung.

Die Schaltflächen verwenden den dedizierten Endpunkt `api.cgi` auf der IPFire-Firewall. Das CGI verwendet die native Verbindungssteuerung und Authentifizierung von IPFire.

### Installation des IPFire-CGI

Das CGI-Skript befindet sich im Repository unter:

```text
ipfire/api.cgi
```

Das CGI muss manuell auf der IPFire-Firewall installiert werden. HACS installiert nur die Home-Assistant-Integration und kann keine Dateien auf das separate IPFire-System kopieren.

Das CGI nach folgendem Pfad kopieren:

```text
/srv/web/ipfire/cgi-bin/api.cgi
```

Anschließend Besitzer und Berechtigungen setzen:

```bash
chown root:root /srv/web/ipfire/cgi-bin/api.cgi
chmod 755 /srv/web/ipfire/cgi-bin/api.cgi
```

Das CGI verwendet die bestehende Authentifizierung der IPFire-Weboberfläche. Es werden keine zusätzlichen CGI-Zugangsdaten benötigt.

**Sicherheit:** Das CGI sollte ausschließlich über die vertrauenswürdige IPFire-Weboberfläche erreichbar sein und darf nicht gegenüber nicht vertrauenswürdigen Netzwerken freigegeben werden.

## Abfrageintervall

Das Abfrageintervall kann zwischen folgenden Werten eingestellt werden:

* **Minimum:** 5 Sekunden
* **Standard:** 30 Sekunden
* **Maximum:** 60 Sekunden

Das Intervall kann in 5-Sekunden-Schritten über den Schieberegler in der Konfiguration eingestellt werden.

Ein kürzeres Intervall sorgt für häufigere Aktualisierungen, führt aber auch zu mehr Anfragen an die IPFire-Firewall.

## SSL-Zertifikate

Die Prüfung des SSL-Zertifikats kann während der Einrichtung aktiviert oder deaktiviert werden.

Da IPFire-Installationen häufig selbst signierte Zertifikate verwenden, ist die Zertifikatsprüfung standardmäßig deaktiviert.

Wenn deine IPFire-Installation ein von einer vertrauenswürdigen Zertifizierungsstelle signiertes Zertifikat verwendet, kann die SSL-Prüfung aktiviert werden.

## Authentifizierung

Der IPFire-Endpunkt `speed.cgi` benötigt eine Authentifizierung.

HA-IPFire unterstützt daher:

* Benutzername
* Passwort

Die Zugangsdaten werden bei der Einrichtung der Integration in Home Assistant angegeben.

## Installation

Direkt über diesen Button:

[![Open HA-IPFire in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FMainz&repository=HA-IPFire&category=integration)
oder mittels HACS.

### HACS

HA-IPFire kann direkt über HACS installiert werden.

1. **HACS** öffnen.
2. **Integrations** auswählen.
3. Nach `HA-IPFire` suchen.
4. Die Integration installieren.
5. Home Assistant neu starten.

Falls HA-IPFire nicht über die normale HACS-Suche verfügbar ist, kann das Repository alternativ als benutzerdefiniertes Repository hinzugefügt werden:

```text
https://github.com/FMainz/HA-IPFire
```

Als Repository-Typ **Integration** auswählen.

Nach der Installation die Integration über:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

hinzufügen.

Nach folgendem Namen suchen:

**HA-IPFire**

### Manuelle Installation

Das folgende Verzeichnis:

```text
custom_components/ipfire
```

nach:

```text
config/custom_components/ipfire
```

kopieren.

Danach Home Assistant neu starten und IPFire über:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

hinzufügen.

## Konfiguration

Während der Einrichtung fragt HA-IPFire nach folgenden Informationen:

* IPFire-URL
* Benutzername
* Passwort
* SSL-Zertifikatsprüfung
* Abfrageintervall

Die Standard-IPFire-URL lautet:

```text
https://ipfire.local:444
```

HA-IPFire verwendet für die Verkehrsdaten automatisch:

```text
/cgi-bin/speed.cgi
```

Für die Steuerung der Internetverbindung wird:

```text
/cgi-bin/api.cgi
```

verwendet.

Das Abfrageintervall kann zwischen **5 und 60 Sekunden** eingestellt werden.

## IPFire-Daten

Die Daten werden direkt aus IPFire ausgelesen. Für die Verkehrsstatistiken
wird `speed.cgi` verwendet. Zusätzliche System-, Netzwerk-, Service- und
Update-Informationen werden über die optionale `api.cgi` bereitgestellt.
Technische Systeminformationen stammen dabei aus Fireinfo.

## Gerät

HA-IPFire erstellt ein gemeinsames IPFire-Gerät in Home Assistant.

Ist `api.cgi` nicht vorhanden, werden ausschließlich folgende Sensoren
bereitgestellt:

* Download
* Upload
* Download Speed
* Upload Speed

Ist `api.cgi` vorhanden, stehen zusätzlich weitere Informationen zum
IPFire-System sowie die Steuerung der Internetverbindung über die Aktionen
`Verbinden` und `Trennen` zur Verfügung.

## Verbindungssteuerung

HA-IPFire kann die Internetverbindung der IPFire-Firewall direkt aus Home Assistant steuern.

Über die bereitgestellten Buttons stehen folgende Aktionen zur Verfügung:

* **Verbinden** – stellt die Internetverbindung her.
* **Trennen** – trennt die Internetverbindung.

Wenn bei bestehender Verbindung `Verbinden` betätigt wird, wird die aktuelle Verbindung getrennt und neu aufgebaut.

## Home Assistant

HA-IPFire ist für aktuelle Home-Assistant-Versionen ausgelegt und verwendet die nativen Sensor-Einheiten und Statistikfunktionen von Home Assistant.

Die kumulativen Trafficzähler werden als kontinuierlich steigende Werte bereitgestellt. Dadurch können sie von Home Assistant für Statistiken und den Verlauf verwendet werden.

## Support

Wenn du einen Fehler findest oder einen Verbesserungsvorschlag hast, kannst du ein Issue im GitHub-Repository erstellen:

https://github.com/FMainz/HA-IPFire/issues

## Repository

https://github.com/FMainz/HA-IPFire

## Lizenz

HA-IPFire wird unter der MIT-Lizenz veröffentlicht.

---
