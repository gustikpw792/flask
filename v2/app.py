from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from . import basic

load_dotenv()

host = os.getenv("OLT_HOST")


app = Flask(__name__)


@app.route("")
def hello_world():
    print("Hello")


@app.route("/v2/onu_state_all", methods=["GET"])
def onu_state_all():
    if request.form.get("interface"):
        telnet_table = basic.show_gpon_state_by_interface(
            host, request.form.get("interface")
        )
    else:
        telnet_table = basic.show_state(host)

    # mengambil data mulai dari index 3 sampai index ke dua dari terakhir
    array = telnet_table.split("\r\n")[3:-2]
    # mengambil index kedua dari terakhir utk mendapatkan 'ONU Number: x/x'
    onu_number = telnet_table.split("\r\n")[-2]
    data = []
    for c in array:
        row = {
            "onu_index": c.split()[0],
            "admin_state": c.split()[1],
            "omcc_state": c.split()[2],
            "phase_state": c.split()[3],
            "channel": c.split()[4],
        }
        data.append(row)

    return jsonify(
        {"data": data, "onu_number": onu_number.replace("ONU Number: ", "").strip()}
    )


if __name__ == "__main__":
    app.run(debug=True)
