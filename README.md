# Analyseur de Données de Débit CEHQ

Cette application récupère les données hydrométriques du Centre d'expertise hydrique du Québec (CEHQ) et les ingère dans une base de données InfluxDB. Elle analyse les mesures de niveau d'eau (niveau) et de débit (débit) pour les stations spécifiées, gérant les données en heure normale de l'Est (EST) et évitant les entrées dupliquées.

## Fonctionnalités

- Récupère les données de l'API publique du CEHQ pour les stations hydrométriques
- Analyse les données CSV avec des délimiteurs de tabulation
- Écrit les données dans InfluxDB avec une gestion appropriée des horodatages
- Ignore les données déjà ingérées pour éviter les doublons
- Prend en charge l'ingestion sélective de champs (niveau et/ou débit)
- Interface en ligne de commande pour une automatisation facile

## Prérequis

- Python 3.12 ou plus récent
- Instance InfluxDB (version 2.x)
- Connexion Internet pour récupérer les données CEHQ

## Installation

1. Cloner ce dépôt :
   ```bash
   git clone https://github.com/tolrahC/CEHQFlow.git
   cd CEHQFlow
   ```

2. Installer les dépendances Python :
   ```bash
   pip install -r python/requirements.txt
   ```

## Utilisation

Exécuter l'analyseur avec les arguments requis :

```bash
python python/cehq_parser.py --station 030106 --url http://localhost:8086 --token <votre-token> --org <votre-org>
```

### Arguments

- `--station` : Numéro de station CEHQ (requis, ex. 030106)
- `--fields` : Champs à ingérer (optionnel, défaut : niveau débit ; choix : niveau, débit)
- `--url` : URL InfluxDB (requis)
- `--token` : Jeton API InfluxDB (requis)
- `--org` : Organisation InfluxDB (requis)
- `--bucket` : Compartiment InfluxDB (optionnel, défaut : hydro)
- `--measurement` : Nom de mesure InfluxDB (optionnel, défaut : streamflow)

Exemple :
```bash
python python/cehq_parser.py --station 030106 --fields niveau --url https://influxdb.example.com:8086 --token abc123 --org myorg --bucket hydro --measurement streamflow
```

## Docker

Un Dockerfile est fourni pour le déploiement conteneurisé.

1. Construire l'image :
   ```bash
   docker build -f docker/dockerfile -t cehq-parser .
   ```

2. Exécuter le conteneur :
   ```bash
   docker run cehq-parser --station 030106 --url http://host.docker.internal:8086 --token <token> --org <org>
   ```

Note : Ajuster l'URL InfluxDB si InfluxDB fonctionne en dehors du conteneur.

## Source de Données

Les données proviennent du système de surveillance hydrométrique public du CEHQ : https://www.cehq.gouv.qc.ca/suivihydro/

- Les données sont au format CSV avec des séparateurs de tabulation
- Les horodatages sont en EST (UTC-5)
- Les champs incluent la date, l'heure, le niveau d'eau (m), et le débit (m³/s)

## TODO

- [ ] Ajouter la prise en charge de bases de données de destination supplémentaires (par ex. PostgreSQL, MySQL, TimescaleDB) au-delà d'InfluxDB

## Licence

Voir [LICENSE](LICENSE)

---

## Version Anglaise

# CEHQ Flow Data Parser

This application fetches hydrometric data from the Centre d'expertise hydrique du Québec (CEHQ) and ingests it into an InfluxDB database. It parses water level (niveau) and flow rate (débit) measurements for specified stations, handling data in Eastern Standard Time (EST) and avoiding duplicate entries.

## Features

- Fetches data from CEHQ's public API for hydrometric stations
- Parses CSV data with tab delimiters
- Writes data to InfluxDB with proper timestamp handling
- Skips already ingested data to prevent duplicates
- Supports selective field ingestion (niveau and/or débit)
- Command-line interface for easy automation

## Prerequisites

- Python 3.12 or later
- InfluxDB instance (version 2.x)
- Internet connection for fetching CEHQ data

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/tolrahC/CEHQFlow.git
   cd CEHQFlow
   ```

2. Install Python dependencies:
   ```bash
   pip install -r python/requirements.txt
   ```

## Usage

Run the parser with the required arguments:

```bash
python python/cehq_parser.py --station 030106 --url http://localhost:8086 --token <your-token> --org <your-org>
```

### Arguments

- `--station`: CEHQ station number (required, e.g., 030106)
- `--fields`: Fields to ingest (optional, default: niveau débit; choices: niveau, débit)
- `--url`: InfluxDB URL (required)
- `--token`: InfluxDB API token (required)
- `--org`: InfluxDB organization (required)
- `--bucket`: InfluxDB bucket (optional, default: hydro)
- `--measurement`: InfluxDB measurement name (optional, default: streamflow)

Example:
```bash
python python/cehq_parser.py --station 030106 --fields niveau --url https://influxdb.example.com:8086 --token abc123 --org myorg --bucket hydro --measurement streamflow
```

## Docker

A Dockerfile is provided for containerized deployment.

1. Build the image:
   ```bash
   docker build -f docker/dockerfile -t cehq-parser .
   ```

2. Run the container:
   ```bash
   docker run cehq-parser --station 030106 --url http://host.docker.internal:8086 --token <token> --org <org>
   ```

Note: Adjust the InfluxDB URL if running InfluxDB outside the container.

## Data Source

Data is sourced from CEHQ's public hydrometric monitoring system: https://www.cehq.gouv.qc.ca/suivihydro/

- Data is in CSV format with tab separators
- Timestamps are in EST (UTC-5)
- Fields include date, time, water level (m), and flow rate (m³/s)

## TODO

- [ ] Add support for additional destination databases (e.g., PostgreSQL, MySQL, TimescaleDB) beyond InfluxDB

## License

See [LICENSE](LICENSE)
