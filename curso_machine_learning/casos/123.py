import json
import ssl
from pathlib import Path

import pandas as pd
import urllib3
from urllib3 import PoolManager


# Crear contexto SSL sin verificación
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


BASE_URL = "https://datosabiertos.bogota.gov.co/api/3/action/datastore_search"
RESOURCE_ID = "599bae63-ab39-4e6c-8abb-f454764c4aa4"


def fetch_all_records(resource_id: str, *, limit: int = 1000) -> pd.DataFrame:
    http = PoolManager(cert_reqs="CERT_NONE", ssl_context=ssl_context)

    offset = 0
    total = None
    all_records: list[dict] = []

    while True:
        url = f"{BASE_URL}?resource_id={resource_id}&limit={limit}&offset={offset}"
        resp = http.request("GET", url)

        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} al consultar datastore_search")

        payload = json.loads(resp.data.decode("utf-8"))
        if not payload.get("success"):
            raise RuntimeError(f"Respuesta no exitosa: {payload}")

        result = payload["result"]
        if total is None:
            total = int(result.get("total", 0))

        records = result.get("records", [])
        all_records.extend(records)

        offset += len(records)
        print(f"Descargados {offset}/{total} registros")

        if not records or offset >= total:
            break

    return pd.DataFrame(all_records)


def main() -> None:
    df = fetch_all_records(RESOURCE_ID, limit=1000)

    out_path = Path(__file__).with_name("datos_bogota_resource_599bae63.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"CSV guardado en: {out_path}")
    print(df.head())


if __name__ == "__main__":
    main()