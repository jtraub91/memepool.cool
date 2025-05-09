import json
import requests
import time
from datetime import datetime
from pathlib import Path
from mimetypes import guess_extension

import bits.crypto
from utils import parse_inscriptions


def run():
    url = "https://mempool.space/api/mempool/txids"
    response = requests.get(url)
    txids = response.json()
    Path("_mempool").mkdir(exist_ok=True)
    timestamp = int(time.time())
    dt = datetime.fromtimestamp(timestamp)
    mempool_snapshot_path = Path(f"_mempool/{dt.strftime('%Y-%m-%d_%H-%M-%S')}")
    mempool_snapshot_path.mkdir()
    for i, txid in enumerate(txids):
        print(f"Processing {i + 1}/{len(txids)} in mempool: {txid}")
        tx_path = mempool_snapshot_path / f"{txid}"
        tx_path.mkdir()

        print(f"Fetching raw bytes for {txid} ...")
        url = f"https://mempool.space/api/tx/{txid}/raw"
        response = requests.get(url)
        tx_ = response.content
        with (tx_path / "raw").open("wb") as f:
            f.write(response.content)

        print(f"Fetching metadata for {txid} ...")
        url = f"https://mempool.space/api/tx/{txid}"
        response = requests.get(url)
        with (tx_path / "meta.json").open("w") as f:
            f.write(response.text)
        try:
            inscriptions = parse_inscriptions(tx_)
        except Exception as e:
            print(f"Error parsing inscriptions for {txid}: {e}")
            inscriptions = None
        if inscriptions:
            print(f"Found {len(inscriptions)} inscriptions in {txid}")
            tx_inscription_path = tx_path / "inscriptions"
            tx_inscription_path.mkdir()
        for inscription in inscriptions:
            content_type = inscription["content_type"]
            content = inscription["data"]
            content_hash = bits.crypto.hash256(content)
            content_size = len(content)

            delegate = inscription.get("delegate")
            metadata = inscription.get("metadata")
            pointer = inscription.get("pointer")
            properties = inscription.get("properties")
            provenance = inscription.get("provenance")

            # parse content type
            content_types = content_type.split(";")
            mime = content_types[0].strip()
            mime_type, mime_subtype = mime.split("/")
            mime_params = {}
            for param in content_types[1:]:
                key, value = param.split("=")
                mime_params[key.strip()] = value.strip()

            if not delegate:
                file_ext = guess_extension(mime)
                if not file_ext:
                    print("WARNING: Couldn't guess extension for {mime}")

                charset = mime_params.get("charset", "utf-8")

                filename = (
                    f"{content_hash.hex()}{file_ext}"
                    if file_ext
                    else content_hash.hex()
                )

                filepath = tx_inscription_path / filename
                with filepath.open("wb") as fp:
                    fp.write(content)
                print(f"{filename} saved to {filepath}")


if __name__ == "__main__":
    run()
