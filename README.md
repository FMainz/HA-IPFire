# HA-IPFire

[🇬🇧 English](#english) · [🇩🇪 Deutsch](#deutsch)

---

<a name="english"></a>

## 🇬🇧 English

Home Assistant integration for monitoring traffic statistics from an IPFire firewall.

## Features

HA-IPFire provides the following features:

* Download traffic counter
* Upload traffic counter
* Current download speed
* Current upload speed
* Configurable polling interval
* Polling interval from 5 to 60 seconds
* Optional SSL certificate verification
* Username/password authentication
* HACS compatible
* German and English translations

## IPFire

The integration retrieves traffic information from the IPFire endpoint:

```text
/cgi-bin/speed.cgi
```

The default URL is:

```text
https://ipfire.local:444
```

The hostname or IP address can be changed during configuration.

HA-IPFire uses the cumulative traffic counters provided by IPFire to calculate the current transfer rates.

## Sensors

The integration provides four sensors:

* **Download**
* **Upload**
* **Download Speed**
* **Upload Speed**

The cumulative traffic counters are provided in bytes.

The current transfer rates are calculated from the difference between two consecutive counter readings and are internally provided in bytes per second.

Home Assistant handles unit conversion and display formatting.

## Polling interval

The polling interval can be configured between:

* **Minimum:** 5 seconds
* **Default:** 30 seconds
* **Maximum:** 60 seconds

A shorter interval provides more frequent updates but also results in more requests to the IPFire firewall.

## SSL certificates

SSL certificate verification can be enabled or disabled during configuration.

Because IPFire installations commonly use self-signed certificates, certificate verification is disabled by default.

If your IPFire installation uses a certificate signed by a trusted certificate authority, SSL verification can be enabled.

## Authentication

The IPFire `speed.cgi` endpoint requires authentication.

HA-IPFire therefore supports:

* Username
* Password

The credentials are configured when adding the integration to Home Assistant.

## Installation

### HACS

HA-IPFire can be installed directly through HACS.

1. Open **HACS**.
2. Select **Integrations**.
3. Search for `HA-IPFire`.
4. Install the integration.
5. Restart Home Assistant.

If HA-IPFire is not available in the standard HACS search, the repository can alternatively be added as a custom repository:

```text
https://github.com/FMainz/HA-IPFire
```

Select **Integration** as the repository type.

After installation, add the integration through:

**Settings → Devices & services → Add integration**

Search for:

**HA-IPFire**

### Manual installation

Copy the following directory:

```text
custom_components/ipfire
```

into:

```text
config/custom_components/ipfire
```

Restart Home Assistant and add IPFire through:

**Settings → Devices & services → Add integration**

## Configuration

During setup, HA-IPFire asks for the following information:

* IPFire URL
* Username
* Password
* SSL certificate verification
* Polling interval

The default IPFire URL is:

```text
https://ipfire.local:444
```

HA-IPFire automatically uses:

```text
/cgi-bin/speed.cgi
```

as the API endpoint.

The polling interval can be configured between **5 and 60 seconds**.

## IPFire data

IPFire provides cumulative traffic counters through `speed.cgi`.

A typical response contains values similar to:

```xml
<inetinfo>
    <rx_kbs>0 kb/s</rx_kbs>
    <tx_kbs>0 kb/s</tx_kbs>
    <rxb>7307842082</rxb>
    <txb>5579282702</txb>
</inetinfo>
```

HA-IPFire uses the cumulative `rxb` and `txb` counters.

The `rx_kbs` and `tx_kbs` values are not used for calculating the current transfer rate.

Instead, the current download and upload speeds are calculated from the difference between two consecutive counter readings.

This also avoids problems with IPFire installations where `rx_kbs` and `tx_kbs` are reported as `0 kb/s`.

## Device

HA-IPFire creates one IPFire device in Home Assistant.

The following sensors are associated with this device:

* Download
* Upload
* Download Speed
* Upload Speed

## Home Assistant

HA-IPFire is designed for current Home Assistant versions and uses Home Assistant's native sensor units and statistics support.

The integration provides cumulative traffic counters as increasing values, allowing Home Assistant to use them for statistics and history.

## Support

If you encounter a problem or have a suggestion, please open an issue in the GitHub repository:

https://github.com/FMainz/HA-IPFire/issues

## Repository

https://github.com/FMainz/HA-IPFire

## License

HA-IPFire is released under the MIT License.

---

<a name="deutsch"></a>

## 🇩🇪 Deutsch

HA-IPFire ist eine Home-Assistant-Integration zur Überwachung von Netzwerkverkehrsstatistiken einer IPFire-Firewall.

## Funktionen

HA-IPFire bietet folgende Funktionen:

* Download-Trafficzähler
* Upload-Trafficzähler
* Aktuelle Download-Geschwindigkeit
* Aktuelle Upload-Geschwindigkeit
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

## Sensoren

Die Integration stellt vier Sensoren bereit:

* **Download**
* **Upload**
* **Download Speed**
* **Upload Speed**

Die kumulativen Trafficzähler werden in Byte bereitgestellt.

Die aktuellen Übertragungsraten werden aus der Differenz zwischen zwei aufeinanderfolgenden Messungen berechnet und intern in Byte pro Sekunde bereitgestellt.

Die Umrechnung der Einheiten und die Darstellung übernimmt Home Assistant.

## Abfrageintervall

Das Abfrageintervall kann zwischen folgenden Werten eingestellt werden:

* **Minimum:** 5 Sekunden
* **Standard:** 30 Sekunden
* **Maximum:** 60 Sekunden

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

HA-IPFire verwendet automatisch:

```text
/cgi-bin/speed.cgi
```

als API-Endpunkt.

Das Abfrageintervall kann zwischen **5 und 60 Sekunden** eingestellt werden.

## IPFire-Daten

IPFire stellt über `speed.cgi` kumulative Trafficzähler bereit.

Eine typische Antwort enthält beispielsweise:

```xml
<inetinfo>
    <rx_kbs>0 kb/s</rx_kbs>
    <tx_kbs>0 kb/s</tx_kbs>
    <rxb>7307842082</rxb>
    <txb>5579282702</txb>
</inetinfo>
```

HA-IPFire verwendet die kumulativen Zähler `rxb` und `txb`.

Die Werte `rx_kbs` und `tx_kbs` werden nicht zur Berechnung der aktuellen Übertragungsrate verwendet.

Stattdessen werden die aktuellen Download- und Upload-Geschwindigkeiten aus der Differenz zwischen zwei aufeinanderfolgenden Messungen der kumulativen Zähler berechnet.

Dadurch werden auch Probleme mit IPFire-Installationen vermieden, bei denen `rx_kbs` und `tx_kbs` immer mit `0 kb/s` zurückgegeben werden.

## Gerät

HA-IPFire erstellt ein gemeinsames IPFire-Gerät in Home Assistant.

Diesem Gerät werden folgende Sensoren zugeordnet:

* Download
* Upload
* Download Speed
* Upload Speed

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
