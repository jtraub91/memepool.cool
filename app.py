from flask import Flask, render_template
from datetime import datetime
import os

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
        os.path.getsize(os.path.join("_mempool", latest, txid)) for txid in txids
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
    with open(os.path.join("_mempool", latest, txid), "rb") as f:
        tx_ = f.read()    
        
    return {"txid": txid, "hex": tx_.hex(), "bin": format(int(tx_.hex(), 16), f'0{len(tx_) * 8}b')}


if __name__ == "__main__":
    app.run(debug=True)
