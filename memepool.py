import requests
import time
from datetime import datetime
from pathlib import Path


def run():
    url = "https://mempool.space/api/mempool/txids"
    response = requests.get(url)
    txids = response.json()
    Path("_mempool").mkdir(exist_ok=True)
    timestamp = int(time.time())
    dt = datetime.fromtimestamp(timestamp)
    mempool_snapshot_path = Path(f"_mempool/{dt.strftime('%Y-%m-%d_%H-%M-%S')}")
    mempool_snapshot_path.mkdir()
    for txid in txids:
        url = f"https://mempool.space/api/tx/{txid}/raw"
        response = requests.get(url)
        with (mempool_snapshot_path / txid).open("wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    run()
