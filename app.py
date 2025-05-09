from flask import Flask, render_template, send_file
from datetime import datetime
import os
import json


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mempool")
def mempool():
    snapshots = os.listdir("_mempool")
    sorted_ = sorted(
        snapshots,
        key=lambda x: datetime.strptime(x.replace("_", " "), "%Y-%m-%d %H-%M-%S"),
        reverse=True,
    )
    latest = sorted_[0]
    txids = os.listdir(os.path.join("_mempool", latest))
    total_size = sum(
        os.path.getsize(os.path.join("_mempool", latest, txid, "raw")) for txid in txids
    )
    return {
        "time": datetime.strptime(latest.replace("_", " "), "%Y-%m-%d %H-%M-%S"),
        "len": len(txids),
        "size": total_size,
        "txids": txids,
    }


@app.route("/tx/<txid>")
def tx(txid):
    snapshots = os.listdir("_mempool")
    sorted_ = sorted(
        snapshots,
        key=lambda x: datetime.strptime(x.replace("_", " "), "%Y-%m-%d %H-%M-%S"),
        reverse=True,
    )
    latest = sorted_[0]
    with open(os.path.join("_mempool", latest, txid, "raw"), "rb") as f:
        tx_ = f.read()
    with open(os.path.join("_mempool", latest, txid, "meta.json"), "r") as f:
        tx_metadata = f.read()
    tx_metadata = json.loads(tx_metadata)
    if os.path.exists(os.path.join("_mempool", latest, txid, "inscriptions")):
        inscriptions = os.listdir(
            os.path.join("_mempool", latest, txid, "inscriptions")
        )
    else:
        inscriptions = None

    return {
        "txid": txid,
        "hex": tx_.hex(),
        "size": len(tx_),
        "metadata": tx_metadata,
        "inscriptions": inscriptions,
    }


@app.route("/tx/<txid>/<inscription_filename>")
def tx_inscription(txid, inscription_filename):
    snapshots = os.listdir("_mempool")
    sorted_ = sorted(
        snapshots,
        key=lambda x: datetime.strptime(x.replace("_", " "), "%Y-%m-%d %H-%M-%S"),
        reverse=True,
    )
    latest = sorted_[0]
    with open(
        os.path.join("_mempool", latest, txid, "inscriptions", inscription_filename),
        "rb",
    ) as f:
        inscription = f.read()
    return send_file(
        os.path.join("_mempool", latest, txid, "inscriptions", inscription_filename),
    )


if __name__ == "__main__":
    app.run(debug=True)
