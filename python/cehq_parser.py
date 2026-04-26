#
# CEHQ → InfluxDB Exporter
# ------------------------
# Fetches hydrometric data (water level, flow rate) from the CEHQ public portal
# and ingests it incrementally into an InfluxDB v2 database.
#
# Usage:
#   python cehq_exporter.py --station 030106 --url http://localhost:8086 \
#                           --token <token> --org <org>
#
#
# Made with help from Claude. Contributions welcome! See GitHub repo for details.
# See README.md for full documentation.

import requests
import csv
import io
import argparse
from datetime import datetime, timezone, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- Column definitions ---
# Maps CLI field names to (column_index, influx_field_name)
FIELDS = {
    "niveau": (2, "niveau_m"),
    "debit":  (4, "debit_m3s"),
}

#CEHQ data are always EST
EST = timezone(timedelta(hours=-5))

def fetch_data(station) -> list[dict]:
    """
    Fetch a station data

    Parameters:
        station (str): Station from which we want to get the data

    Returns:
        list[dict]: Data of the station.

    """
    url = f"https://www.cehq.gouv.qc.ca/suivihydro/fichier_donnees.asp?NoStation={station}"
    resp = requests.get(url, timeout=30)
    resp.encoding = "latin-1"

    rows = []
    reader = csv.reader(io.StringIO(resp.text), delimiter="\t")
    for row in reader:
        if len(row) < 5 or not row[0].strip().startswith("20"):
            continue
        rows.append(row)
    return rows

def parse_and_write(station, fields, influx_url, token, org, bucket, measurement):
    """
    Parse extracted data and write it to InfluxDB

    Parameters:
        station (str): Station from which we want to get the data
        fields (str): Field list we want to parse
        influx_url (str): InfluxDB API URL
        token (str): InfluxDB API token
        org (str): InfluxDB Organization
        bucket (str): InfluxDB Bucket
        measurement (str): InfluxDB Measurement

    """
    rows = fetch_data(station)

    print(f"Raw rows fetched: {len(rows)}")

    with InfluxDBClient(url=influx_url, token=token, org=org) as client:

        latest = get_latest_timestamp(client, org, bucket, station, measurement)
        if latest:
            print(f"Latest record in InfluxDB: {latest} — skipping older data")

        points = []
        for row in rows:
            date_str = row[0].strip()
            time_str = row[1].strip()

            try:
                ts = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=EST)
            except ValueError:
                continue

            # Skip if already stored
            if latest and ts <= latest:
                continue

            point = Point(measurement).tag("station", station)
            valid = False

            for field in fields:
                col_index, influx_name = FIELDS[field]
                try:
                    value = float(row[col_index].strip().replace(",", "."))
                    point.field(influx_name, value)
                    valid = True
                except (ValueError, IndexError):
                    pass

            if valid:
                point.time(ts, "s")
                points.append(point)

        print(f"Writing {len(points)} new records for station {station}")

        if points:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=bucket, record=points)
            print("Done.")
        else:
            print("Nothing new to write.")

def get_latest_timestamp(client, org, bucket, station, measurement):
    """
    Get the latest timestamp in InfluxDB for the station

    Parameters:
        client (InfluxDBClient): InfluxDB client
        org (str): InfluxDB Organization
        bucket (str): InfluxDB Station
        station (str): CEHQ Station number
        measurement (str): InfluxDB Measurement

    Returns:
        datetime: Timezone-aware datetime, or None if no data yet

    """
    query_api = client.query_api()
    query = f'''
        from(bucket: "{bucket}")
          |> range(start: -1y)
          |> filter(fn: (r) => r._measurement == "{measurement}")
          |> filter(fn: (r) => r.station == "{station}")
          |> last()
    '''
    tables = query_api.query(query, org=org)
    latest = None
    for table in tables:
        for record in table.records:
            if latest is None or record.get_time() > latest:
                latest = record.get_time()
    return latest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest CEHQ hydrometric data into InfluxDB")

    parser.add_argument("--station",  required=True,              help="CEHQ station number, e.g. 030106")
    parser.add_argument("--fields",   nargs="+", default=["niveau", "debit"],
                        choices=FIELDS.keys(),                     help="Fields to ingest (default: both)")
    parser.add_argument("--url",      required=True, help="InfluxDB URL")
    parser.add_argument("--token",    required=True,              help="InfluxDB token")
    parser.add_argument("--org",      required=True,              help="InfluxDB org")
    parser.add_argument("--bucket",   default="hydro",            help="InfluxDB bucket (default: hydro)")
    parser.add_argument("--measurement",    default="streamflow",   help="InfluxDB measurement")

    args = parser.parse_args()
    parse_and_write(args.station, args.fields, args.url, args.token, args.org, args.bucket, args.measurement)