import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import re
import os
import basic
import routers
# import db
import parse_stdout as parse

os.environ['FLASK_RUN_PORT'] = '5002'
# from urllib.parse import unquote

# Load variabel lingkungan dari file .env
load_dotenv()

host = os.getenv("OLT_HOST")


app = Flask(__name__)


@app.route("/ping")
def ping():
    return 'pong'

@app.route("/")
def hello_world():
    return 'hello world'

@app.route("/v1/backup_cfg/", methods=["POST"])
def backup_cfg():
    data = {
        'routerip' :    request.form.get("routerip"),
        'routeruser':   request.form.get('routeruser'),
        'routerpass':   request.form.get('routerpass')
    }

    olt = basic.backup_config(host, data)

    return jsonify({'message' : olt})



@app.route("/v1/onuadd", methods=["POST"])
def onuadd():
    # for host in hosts:
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
        # add PPP Secret Mikrotik
        # create secret disabled. php already make it
        # mtik = routers.add_ppp_secret(
        #     post_data["username"], post_data["password"], access_mode, ppp_profile
        # )

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
    

@app.route("/v1/reconfig_onu", methods=["POST"])
def reconfig_onu():

    post_data = {
        "gpon_olt": str(request.form.get("gpon_olt")),
        "onu_index": str(request.form.get("onu_index")),
        "onu_type": request.form.get("onu_type"),
        "sn": request.form.get("sn"),
        "gpon_onu": request.form.get("gpon_onu"),
        "name": request.form.get("name"),
        "description": request.form.get("description"),
        "access_mode": "pppoe",
        "username": request.form.get("username"),
        "password": request.form.get("password"),
        "mode_config": request.form.get("mode_config"),
        "vlan_profile": request.form.get("vlan_profile"),
        "cvlan": request.form.get("cvlan"),
        "tcont" : request.form.get("tcont"),
        "gemport" : request.form.get("gemport")
    }

    regis = basic.onuadd(host, post_data)

    if regis.__contains__("#"):
        return jsonify(
            {
                "message_olt": "Registering onu " + post_data["gpon_onu"] + " success!",
                "status": True,
                "data": {
                    "name": post_data["name"],
                    "username": post_data["username"],
                    "password": post_data["password"],
                    "gpon_onu": post_data["gpon_onu"],
                },
            }
        )
    else:
        return jsonify(
            {
                "message": "An error occurred while adding ONU " + post_data["gpon_onu"] + "!",
                "status": False,
            }
        )


@app.route("/v1/remove_onu", methods=["DELETE"])
def removeonu():
    gpon_olt = str(request.form.get("gpon_olt"))
    onu_index = str(request.form.get("onu_index"))

    data = {"gpon_olt": gpon_olt, "onu_index": onu_index}

    delete = basic.delete_onu(host, data)

    if delete.__contains__("[Successful]"):
            return jsonify(
                {
                    "message": "Deleting onu " + gpon_olt + ":" + onu_index + " success!",
                    "status" : True
                }
            )
    else:
        return jsonify(
            {
                "message": "An error occurred while deleting ONU " + gpon_olt + ":" + onu_index,
                "status" : False
            }
        )
    

@app.route("/v1/no_onu", methods=["DELETE"])
def noonu():
    # for host in hosts:
    gpon_olt = str(request.form.get("gpon_olt"))
    onu_index = str(request.form.get("onu_index"))
    # username = str(request.form.get("username"))

    data = {"gpon_olt": gpon_olt, "onu_index": onu_index}

    delete = basic.delete_onu(host, data)

    if delete.__contains__("[Successful]"):
        # delete PPP Secret Mikrotik
        # mtik = routers.del_ppp_secret(username)
        # if mtik['status'] == True :
        return jsonify(
            {
                "message": "Deleting onu "
                + gpon_olt
                + " index "
                + onu_index
                + " success!"
            }
        )
        # else:
        #     return jsonify(
        #         {
        #             "message": "Deleting onu "
        #             + gpon_olt
        #             + " index "
        #             + onu_index
        #             + " success but error deleting username in Router."
        #         }
        #     )
    else:
        return jsonify(
            {
                "message": "An error occurred while deleting ONU "
                + gpon_olt
                + " index "
                + onu_index
                + "!"
            }
        )


@app.route("/v1/restore_factory/", methods=["POST"])
def restorefactory():
    gpon_onu = request.form.get("gpon_onu")

    olt = basic.restore_factory(host, gpon_onu)

    if olt.__contains__("ZXAN#"):
        return jsonify({"message": "Reset Factory ONU berhasil"})
    else:
        return jsonify({"message": "An error occurred while reseting onu!"})


@app.route("/v1/remote_onu/", methods=["POST"])
def remoteonu():
    # for host in hosts:
    gpon_onu = request.form.get("gpon_onu")
    state = request.form.get("remote_state")

    data = {"gpon_onu": gpon_onu, "state": state}

    # open security management 212
    remote = basic.remote_onu(host, data)

    if state == "enable":
        if remote.__contains__("ZXAN#"):
            # get ip address
            ip = getiphost(host, gpon_onu, host_id="1")["current_ip_address"]
            return jsonify(
                {
                    "message": "Anda dapat Remote ONU melalui http://" + ip,
                    "ip_address": ip,
                    "state": state,
                }
            )
        else:
            return jsonify(
                {
                    "message": "An error occurred while enable forward web management!",
                    "ip_address": "",
                    "state": "",
                }
            )
    if state == "disable":
        if remote.__contains__("ZXAN#"):
            return jsonify(
                {"message": "Remote ONU disabled!", "ip_address": "", "state": state}
            )
        else:
            return jsonify(
                {
                    "message": "An error occurred while disable forward web management!",
                    "ip_address": "",
                    "state": "",
                }
            )


@app.route("/v1/getnewindex")
def getnewindex():
    # ex. http://127.0.0.1:5000/v1/getnewindex
    interface = str(request.form.get("interface"))

    return jsonify(getNewIndexby(host, interface))


@app.route("/v1/rawiphost")
def rawiphost():
    gpon_onu = str(request.form.get("gpon_onu"))
    host_id = str(request.form.get("host_id"))
    raw_data = basic.show_gpon_iphost(host, gpon_onu, host_id)
    return raw_data


@app.route("/v1/rawwanip")
def rawwanip():
    gpon_onu = str(request.form.get("gpon_onu"))
    raw_data = basic.show_gpon_wanip(host, gpon_onu)
    return raw_data


@app.route("/v1/rawdetailinfo")
def rawdetailinfo():
    gpon_onu = str(request.form.get("gpon_onu"))
    raw_data = basic.show_onu_detail_info(host, gpon_onu)
    return raw_data


@app.route("/v1/rawonurun")
def rawonurun():
    gpon_onu = str(request.form.get("gpon_onu"))
    return basic.show_onu_run_config(host, gpon_onu)

@app.route("/v1/rawonurunconfinterface")
def rawonurunconfinterface():
    gpon_onu = str(request.form.get("gpon_onu"))
    return basic.show_onu_running_config_interface(host, gpon_onu)


@app.route("/v1/rawshowcard")
def rawshowcard():
    return jsonify(basic.show_card(host))

@app.route("/v1/rawshowgpononuprofilevlan")
def rawshowgpononuprofilevlan():
    return jsonify(basic.show_gpon_onu_profile_vlan(host))


@app.route("/v1/rawshowvlansummary")
def rawshowvlansummary():
    return jsonify(basic.show_vlan_summary(host))


@app.route("/v1/rawshowgponprofiletcont")
def rawshowgponprofiletcont():
    return jsonify(basic.show_gpon_profile_tcont(host))


@app.route("/v1/rawshowgponprofiletraffic")
def rawshowgponprofiletraffic():
    return jsonify(basic.show_gpon_profile_traffic(host))


@app.route("/v1/rawshowonutype")
def rawshowonutype():
    return jsonify(basic.show_onu_type(host))


@app.route("/v1/rawshowiproute")
def rawshowiproute():
    return jsonify(basic.show_ip_route(host))


@app.route("/v1/rawshowgpononubysn")
def rawshowgpononubysn():
    sn = str(request.form.get("sn"))
    return jsonify(basic.show_gpon_onu_by_sn(host, sn))


@app.route("/v1/rawshowgpononustateby", methods=["POST"])
def rawshowgpononustateby():
    gpon_olt = str(request.form.get("gpon_olt"))
    return jsonify(basic.show_gpon_state_by_interface(host, gpon_olt))


@app.route("/v1/reboot", methods=["POST"])
def reboot():
    gpon_onu = str(request.form.get("gpon_onu"))
    raw_data = basic.reboot(host, gpon_onu)

    if raw_data.__contains__("ZXAN#"):
        return jsonify({"message": "Reboot {} success!".format(gpon_onu)})
    else:
        return jsonify(
            {"message": "Error Reboot {}! \nData: {}".format(gpon_onu, raw_data)}
        )


@app.route("/v1/onustate")
def onustate():
    # for host in hosts:
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
    # interfaces = []
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
        {
            "data": data, 
            "onu_number": onu_number.replace("ONU Number: ", "").strip(),
            # "interfaces": interfaces
        }
    )


@app.route("/v1/unconfig")
def uncfg():
    # for host in hosts:
    telnet_output = basic.show_pon_onu_uncfg(host)
    telnet_outputx = """
        OltIndex            Model                    SN                     
        -------------------------------------------------------------------------
        gpon-olt_1/1/3      F609V5.3                 ZTEGC86587D8   --> index 3
        gpon-olt_1/1/4      F609V5.4                 ZTEGC86587D7   --> index -1
        ZXAN#
        """

    if telnet_output.__contains__("No related information to show."):
        return jsonify(
            {"data": [], "message": "No related information to show.", "status": "404"}
        )
    else:
        data = []
        # ambil data mulai dari index 3 dan data sebelum index akhir
        array = telnet_output.split("\r\n")[3:-1]
        for c in array:
            if len(c.split()) == 3 :
                row = {
                    "interface": c.split()[0].replace("gpon-olt_", ""),
                    "model": c.split()[1],
                    "sn": c.split()[2],
                }
            else:
                # jika model ont memiliki 2 kata. Eg. XPON GGC665
                row = {
                    "interface": c.split()[0].replace("gpon-olt_", ""),
                    "model": c.split()[1] + " " + c.split()[2],
                    "sn": c.split()[3],
                }
            data.append(row)

        found = str(len(data)) + " Unconfig found(s)"

        return jsonify({"data": data, "message": found, "status": "200"})


@app.route("/v1/createuserpass")
def pppoeuserpass():
    name = request.form.get("name")
    sn = request.form.get("sn")

    return jsonify(create_user_pass(name, sn))


def create_user_pass(name, sn):
    # ZTEGC91CF46E
    # 501. GREIS RAMPALINO
    # .C91CF46E!
    # 501.-GREIS-RAMPC91C38DD
    # cara untuk membuat username pppoe
    # 1. ganti (spasi) menjadi '-' <--> 501.-GREIS-RAMPALINO
    # 2. ambil 15 karakter no 1 dari depan <--> 501.-GREIS-RAMP
    # 3. ambil 8 karakter serial ont dari belakang  <--> C91CF46E
    # 4. gabungkan no 2 dan 3 menjadi 501.-GREIS-RAMPC91CF46E
    # sn = 'ZTEGC91C715E'
    # name = 'APIN'
    # http://127.0.0.1:5000/v1/createuserpass/ZTEGC91C715E/APIN

    removespace = re.sub(r"\s", "-", name)

    username = removespace[:15] + sn[-8:]
    password = "." + sn[-8:] + "!"

    return {"username": username, "password": password}


# @app.route("/v1/iphost")
# def iphost():
#     gpon_onu = request.form.get('gpon_onu')
#     host_id = request.form.get('host_id')

#     # data = getiphost(host, gpon_onu, host_id)

#     return jsonify(data)


@app.route("/v1/getponpower")
def ponpower():
    # ex. http://127.0.0.1:5000/v1/getponpower/1%2F1%2F1%3A3
    interface = request.form.get("interface")
    return jsonify(getponpower(host, interface))


@app.route("/v1/getponpowerbyinterface")
def getponpowerbyinterface():
    # ex. http://127.0.0.1:5000/v1/getponpower/1%2F1%2F1%3A3
    interface = request.form.get("interface")
    return jsonify(basic.show_pon_power_onurx(host, interface))


@app.route("/v1/getrawponpower")
def rawponpower():
    # ex. http://127.0.0.1:5000/v1/getrawponpower/1%2F1%2F1%3A3
    interface = str(request.form.get("interface"))
    raw_data = basic.show_pon_power_attenuation(host, interface)
    return raw_data.replace("ZXAN#", "\r\n")


@app.route("/v1/getrawgponbaseinfo")
def getrawgponbaseinfo():
    interface = str(request.form.get("interface"))
    raw_data = basic.show_gpon_onu_baseinfo(host, interface)
    return raw_data
    return jsonify(raw_data)


@app.route("/v1/getonu_distance")
def onudistance():
    # ex. http://127.0.0.1:5000/v1/getonu_distance
    # for host in hosts:
    interface = request.form.get("interface")
    return jsonify(onu_distance(host, interface))


def onu_distance(host, interface):
    raw_data = basic.show_gpon_onu_distance(host, interface)

    # Buang karakter newline dan whitespace di awal dan akhir string
    data = raw_data.strip()

    # Split string menjadi list berdasarkan newline
    lines = data.split("\r\n")

    parts = lines[2].split()

    x = {
        "eqd": parts[0],
        "distance": parts[1],
    }

    return x


@app.route("/v1/getrun")
def runc():
    # http://127.0.0.1:5000/v1/getrun
    return jsonify(getrun(host))


@app.route("/v1/ppp_profile")
def ppp_profile():
    # http://127.0.0.1:5000/v1/ppp_profile
    data = routers.ppp_profile()
    return jsonify(data)


@app.route("/v1/vlanprofile")
def vlanprofile():
    # http://127.0.0.1:5000/v1/vlanprofile
    # for host in hosts:
    raw_data = basic.show_gpon_onu_profile_vlan(host)

    # Mencari pola yang sesuai dengan data telnet
    pattern = r"Profile name:\s+(\w+)\r\nTag mode:\s+(\w+)\r\nCVLAN:\s+(\d+)\r\nCVLAN priority:(\d+)"

    # Melakukan pencarian pada data telnet dengan menggunakan pola
    matches = re.search(pattern, raw_data)

    # Membuat dictionary dengan menggunakan key dari pola dan value dari hasil pencarian
    data = {
        "profile_name": matches.group(1),
        "tag_mode": matches.group(2),
        "cvlan": int(matches.group(3)),
        "cvlan_priority": int(matches.group(4)),
    }

    return jsonify(data)


@app.route("/v1/onutype")
def onutype():
    # http://127.0.0.1:5000/v1/onutype
    # for host in hosts:
    raw_data = basic.show_onu_type(host)
    # return jsonify(raw_data)

    results = []

    # menggunakan re.findall() untuk mencari semua kemunculan "ONU type name:"
    matches = re.findall(r"ONU type name:\s*(.*?)\s*\r", raw_data)

    # iterasi setiap hasil yang ditemukan dan tambahkan ke dalam list results sebagai dict
    for match in matches:
        results.append({"onu_type": match})
    return jsonify(results)


def getiphost(hosts, gpon_onu, host_id):
    # for host in hosts:
    raw_data = basic.show_gpon_iphost(host, gpon_onu, host_id)

    # Split the string into lines
    lines = raw_data.split("\r\n")

    # Remove the empty lines and the last line which does not contain any data
    lines = [line for line in lines if line and line != "ZXAN#"]

    # Create an empty dictionary
    ip_dict = {}

    # Loop through the lines and extract the data
    for line in lines:
        key_value = line.split(":")
        key = key_value[0].strip().lower().replace(" ", "_")  # modify the key
        value = key_value[1].strip()
        ip_dict[key] = value

    # if option == 'IP':
    #     # Get the value for the "Current IP address" key
    #     current_ip = ip_dict["current_ip_address"]
    # else:
    return ip_dict


def getstate(host):
    # for host in hosts:
    telnet_table = basic.show_state(host)

    # contoh tabel telnet
    telnet_tablex = """OnuIndex   Admin State  OMCC State  Phase State  Channel    
        --------------------------------------------------------------
        1/1/1:1     enable       enable      working      1(GPON)
        1/1/1:2     enable       enable      working      1(GPON)
        1/1/1:17    enable       disable     DyingGasp    1(GPON)
        """
    # total ONUs
    pattern = r"ONU Number: (\d+/\d+)"
    result_onu = re.search(pattern, telnet_table)
    print("Jumlah total ONU:", result_onu)

    # definisikan pola regex untuk mengambil setiap kolom
    pattern = r"^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$"

    # buat list kosong untuk menampung hasil konversi
    result = []

    # loop tiap baris pada tabel telnet
    for line in telnet_table.split("\n"):
        # gunakan re.sub untuk mengganti spasi berlebih dengan satu spasi
        clean_line = re.sub("\s+", " ", line).strip()
        # gunakan re.match untuk mencocokan dengan pola regex
        match = re.match(pattern, clean_line)
        if match:
            # buat dictionary untuk tiap baris
            row = {
                "onuu_index": match.group(1),
                "admin_state": match.group(2),
                "omcc_state": match.group(3),
                "phase_state": match.group(4),
                "channel": match.group(5),
            }
            # tambahkan dictionary ke dalam list result
            result.append(row)
    return result


def getcard(host):
    # for host in hosts:
    data = basic.show_card(host)
    return parse.to_list(data, "INSERVICE")

@app.route("/v1/wpa", methods=["POST"])
def wpa():
    gpon_onu = request.form.get("gpon_onu")
    ssid = request.form.get("ssid")
    wpa_key = request.form.get("wpa_key")
    mode = request.form.get("mode")

    data = {
        "gpon_onu": gpon_onu,
        "ssid": ssid,
        "wpa_key": wpa_key,
    }

    if mode == 'both' or mode == 'ssid' or mode == 'wpa_key':
        send = basic.change_wpa(host, data, mode)
        
        if send.__contains__("ZXAN#"):
            if mode == 'wpa_key':
                msg = "Success change WPA Key"
            if mode == 'ssid':
                msg = "Success change SSID"
            if mode == 'both':
                msg = "Success change SSID and WPA Key"

            return jsonify({
                "message": msg,
                "status": 200,
            })
        else:
            return jsonify({
                "message": "Some error while change WPA",
                "status": 500,
            })
    else:
        return jsonify({
                "message": "No change be made",
                "status": 404,
            })
    
@app.route("/v1/getTcont", methods=["GET"])
def getTcont():
    data = basic.show_gpon_profile_tcont(host)
    # profiles = re.findall(r'Profile name :([^\s+\r\n]+)', data)
    # Mencari semua Profile name
    profile_names = re.findall(r'Profile name :(\S+)', data)

    # Mencari semua Type (angka di kolom pertama setelah header)
    types = re.findall(r'Type\s+FBW\(kbps\).*?\r\n\s*(\d+)', data, re.DOTALL)

    # Menggabungkan hasil
    result = [{"profile_name": name, "type": type_} 
            for name, type_ in zip(profile_names, types)]

    
    return jsonify(result)


def getponpower(host, interface):
    # http://127.0.0.1:5000/v1/getponpower/1%2F1%2F3%3A5
    # for host in hosts:
    table = basic.show_pon_power_attenuation(host, interface)
    tablex = """           OLT                  ONU              Attenuation
        --------------------------------------------------------------------------
        up      Rx :-33.010(dbm)      Tx:2.724(dbm)        35.734(dB)
        
        down    Tx :8.164(dbm)        Rx:-25.088(dbm)      33.252(dB)"""

    # proses output untuk mengambil nilai 'Rx :'
    uprx_value = uptx_value = downtx_value = downrx_value = ""
    for line in table.split("\n"):
        if "Rx :" in line:
            uprx_value = line.split("Rx :")[1].split("(")[0].strip()
        if "Tx:" in line:
            uptx_value = line.split("Tx:")[1].split("(")[0].strip()
        if "Tx :" in line:
            downtx_value = line.split("Tx :")[1].split("(")[0].strip()
        if "Rx:" in line:
            downrx_value = line.split("Rx:")[1].split("(")[0].strip()
    data = {
        "onu_rx": downrx_value,
        "olt_tx": downtx_value,
        "olt_rx": uprx_value,
        "onu_tx": uptx_value,
    }
    return data


def getrun(host):
    # for host in hosts:
    raw_data = basic.show_run(host)

    # mencari setiap interface dan data name serta description-nya

    interfaces = re.findall(
        r"interface gpon-onu_(\d+/\d+/\d+:\d+)\r\n\s+name (.+)\r\n\s+description (.+)\r\n",
        raw_data,
    )

    result = []
    for interface in interfaces:
        data = {
            "interface": interface[0],
            "name": interface[1],
            "description": interface[2],
        }
        result.append(data)

    # regex untuk mencari data
    interfacesx = re.findall(
        r"pon-onu-mng gpon-onu_(\d+/\d+/\d+:\d+)\r\n\s+.*\s+wan-ip 1 mode (\S+) username (\S+) password (\S+)!",
        raw_data,
    )
    # print(interfacesx)
    # buat output json
    auth = []

    for interfacex in interfacesx:
        auth.append(
            {
                "interface": interfacex[0],
                "mode": interfacex[1],
                "username": interfacex[2],
                "password": interfacex[3],
            }
        )

    data_return = {"data": result, "authentication": auth}

    return data_return


def getunconfig(host):
    # for host in hosts:
    telnet_output = basic.show_pon_onu_uncfg(host)
    telnet_outputx = """
        OltIndex            Model                    SN                     
        -------------------------------------------------------------------------
        gpon-olt_1/1/3      F609V5.3                 ZTEGC86587D8   --> index 3
        gpon-olt_1/1/4      F609V5.4                 ZTEGC86587D7   --> index -1
        ZXAN#
        """

    if telnet_output.__contains__("No related information to show."):
        return jsonify({"data": [], "message": "No related information to show."})
    else:
        data = []
        # ambil data mulai dari index 3 dan data sebelum index akhir
        coba = telnet_output.split("\r\n")[3:-1]
        for c in coba:
            row = {
                "interface": c.split()[0].replace("gpon-olt_", ""),
                "model": c.split()[1],
                "sn": c.split()[2],
            }
            data.append(row)
        return jsonify({"data": data, "message": "Unconfig found(s)"})



# @app.route("/v1/getnewindexby")
def getNewIndexby(host, interface):
    # for host in hosts:
    # interface = str(request.form.get("interface"))

    data = basic.show_gpon_state_by_interface(host, interface)
    
    if data.__contains__("No related information to show."):
        return {"new_index": 1, "registration_onu": interface + ":1"}
    else:
        # Cari semua indeks setelah tanda ':' dan kumpulkan dalam list
        index_list = [int(match.group(1)) for match in re.finditer(r'\d+/\d+/\d+\:(\d+)', data)]

        # Pengecekan indeks yang terlewati
        missing_indexes = []
        for i in range(1, max(index_list) + 1):
            if i not in index_list:
                missing_indexes.append(i)

        # Jika tidak ada indeks yang terlewati, ambil indeks terakhir + 1
        newinterface = interface.replace("gpon-olt_", "")
        if not missing_indexes:
            next_index = max(index_list) + 1
            return {
                        "new_index": next_index,
                        "registration_onu": newinterface + ":" + str(next_index),
                    }
        else:
            next_index = missing_indexes[0]
            return {
                        "new_index": next_index,
                        "registration_onu": newinterface + ":" + str(next_index),
                    }





if __name__ == "__main__":
    app.run(debug=True)
