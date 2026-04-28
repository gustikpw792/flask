from flask import Blueprint, jsonify, request
import time
from dotenv import load_dotenv
import re
import os
import basic
import routers
# import db
import parse_stdout as parse

# Buat blueprint untuk v1
bp_v1 = Blueprint('v1', __name__, url_prefix='/v1')


@bp_v1.route("/v1/onuadd", methods=["POST"])
def onuadd():
    # for host in hosts:
    #data olt
    olt_host = request.form.get("olt_host")
    olt_user = request.form.get("olt_user")
    olt_pass = request.form.get("olt_pass")
    olt_port = request.form.get("olt_port")


    gpon_olt = request.form.get("gpon_olt")
    onu_type = request.form.get("onu_type")
    sn = request.form.get("sn")
    name = request.form.get("name")
    description = request.form.get("description")
    ppp_profile = request.form.get("ppp_profile")
    access_mode = request.form.get("access_mode")
    vlan_profile = request.form.get("vlan_profile")
    cvlan = request.form.get("cvlan")
    tcont = request.form.get("tcont")
    gemport = request.form.get("gemport")

    index_onu = getNewIndexby(host, gpon_olt)
    auth = create_user_pass(name, sn)

    post_data = {
        "gpon_olt": gpon_olt,
        "onu_type": onu_type,
        "sn": sn,
        "name": name,
        "description": description,
        "onu_index": str(index_onu["new_index"]),
        "gpon_onu": index_onu["registration_onu"],
        "access_mode": "pppoe",
        "vlan_profile": vlan_profile,
        "tcont": tcont,
        "gemport": gemport,
        "cvlan": cvlan,
        "username": auth["username"],
        "password": auth["password"],
    }

    if onu_type == 'FIBERHOME' :
        regis = basic.onuaddFiberhome(host, post_data)
    else:
        regis = basic.onuadd(host, post_data)

    # tunggu 8 detik pon modem melakukan lock (ditandai dgn lampu pon berhenti berkedip)
    # time.sleep(8)
    # distance = onu_distance(host, post_data["gpon_onu"])["distance"]
    # time.sleep(2)
    # onu_rx = getponpower(host, post_data["gpon_onu"])["onu_rx"]

    if regis.__contains__("ZXAN#"):
        return jsonify(
            {
                "message_olt": "Registering onu " + post_data["gpon_onu"] + " success!",
                "message_mikrotik": "mtik['message']",
                "data": {
                    "name": post_data["name"],
                    "username": post_data["username"],
                    "password": post_data["password"],
                    "gpon_onu": post_data["gpon_onu"],
                    "ppp_profile": ppp_profile,
                    "description": post_data["description"],
                    # "distance": str(distance),
                    # "rxdb": str(onu_rx),
                },
                "status": "200",
            }
        )
    else:
        return jsonify(
            {
                "message": "An error occurred while adding ONU "
                + post_data["gpon_onu"]
                + "!",
                "message_mikrotik": "",
                "data": {
                    "name": post_data["name"],
                    "username": post_data["username"],
                    "password": post_data["password"],
                    "gpon_onu": post_data["gpon_onu"],
                },
                "status": "404",
            }
        )
    
