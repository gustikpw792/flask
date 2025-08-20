from telnetlib import Telnet
from dotenv import load_dotenv
import time
import re
import os

# host = '10.10.10.2'
load_dotenv()

username = os.getenv("OLT_USER")
password = os.getenv("OLT_PASS")
olt_port = os.getenv("OLT_PORT")

def session(host):
    tn = Telnet(host,olt_port)

    tn.read_until(b'Username:')
    tn.write(username.encode('ascii') + b'\n')

    tn.read_until(b'Password:')
    tn.write(username.encode('ascii') + b'\n')

    tn.read_until(b'#')
    return tn

def backup_config(host, data):
    # file upload cfg startrun.dat ftp ipaddress 192.168.50.1 path /flash user mknet password 1mknet*1
    tn = session(host)

    cmd = """

    file upload cfg startrun.dat ftp ipaddress {} path /flash user {} password {}

    """.format(data['routerip'], data['routeruser'], data['routerpass'])

    tn.write(cmd.encode('ascii'))
    # time.sleep(2)

    return tn.read_until(b'......Successfully').decode('utf-8')

def show_users(host):
    tn = session(host)

    tn.write(b'show users\n')

    stdout = tn.read_until(b'#').decode('utf-8')
    return (stdout)


def show_state(host):
    tn = session(host)

    tn.write(b"terminal length 0\n")
    time.sleep(0.2)

    tn.read_until(b'#')
    tn.write(b'show gpon onu state\n')
    time.sleep(1.5)

    return tn.read_very_eager().decode('utf-8')


def show_run(host):
    tn = session(host)

    tn.write(b"terminal length 0\n")
    time.sleep(0.05)
    tn.read_until(b'#')
    
    tn.write(b'show run\n')
    # time.sleep(4)

    return tn.read_very_eager().decode('utf-8')


def show_card(host):
    tn = session(host)

    tn.write(b'show card\n')
    time.sleep(0.2)

    data = tn.read_until(b'#').decode('utf-8')

    return data


def show_gpon_onu_profile_vlan(host):
    tn = session(host)

    tn.write(b'show gpon onu profile vlan\n')
    time.sleep(0.2)

    return tn.read_until(b'#').decode('utf-8')


def show_gpon_profile_tcont(host):
    tn = session(host)

    tn.write(b'show gpon profile tcont\n')
    time.sleep(0.2)

    return tn.read_until(b'#').decode('utf-8')


def show_gpon_profile_traffic(host):
    tn = session(host)

    tn.write(b'show gpon profile traffic\n')
    time.sleep(0.2)

    return tn.read_until(b'#').decode('utf-8')


def show_vlan_summary(host):
    tn = session(host)

    tn.write(b'show vlan summary\n')
    time.sleep(0.2)

    return tn.read_until(b'#').decode('utf-8')


def show_ip_route(host):
    tn = session(host)

    tn.write(b'show ip route\n')
    time.sleep(0.2)

    return tn.read_until(b'#').decode('utf-8')


def show_pon_power_attenuation(host, interface):
    tn = session(host)

    tn.write(b'show pon power attenuation gpon-onu_' +
             interface.encode('ascii') + b'\n')

    return tn.read_until(b'#').decode('utf-8')


def show_pon_power_onurx(host, interface):
    tn = session(host)
    tn.write(b"terminal length 0\n")
    time.sleep(0.05)
    tn.read_until(b'#').decode('utf-8')

    tn.write(b'show pon power onu-rx gpon-olt_' +
             interface.encode('ascii') + b'\n')
    # time.sleep(2)

    return tn.read_until(b'#').decode('utf-8')
    # return tn.read_very_eager().decode('utf-8')
    # return tn.read_until().decode('utf-8')


def show_onu_run_config(host, interface):
    tn = session(host)

    tn.write(b'show onu running config gpon-onu_' +
             interface.encode('ascii') + b'\n')
    # time.sleep(0.2)

    data = tn.read_until(b'#').decode('utf-8')

    return data


def show_gpon_iphost(host, interface, host_id):
    tn = session(host)

    tn.write(b"terminal length 0\n")
    time.sleep(0.05)

    tn.read_until(b'#')
    tn.write(b'show gpon remote-onu ip-host gpon-onu_' +
             interface.encode('ascii') + b' ' + host_id.encode('ascii') + b'\n')
    time.sleep(0.1)

    data = tn.read_until(b'#').decode('utf-8')
    return data


def show_gpon_wanip(host, interface):
    tn = session(host)

    tn.write(b"terminal length 0\n")
    time.sleep(0.05)

    tn.read_until(b'#')
    tn.write(b'show gpon remote-onu wan-ip gpon-onu_' +
             interface.encode('ascii') + b'\n')
    time.sleep(0.1)

    data = tn.read_until(b'#').decode('utf-8')
    return data


def show_onu_detail_info(host, interface):
    tn = session(host)

    tn.write(b"terminal length 0\n")
    time.sleep(0.05)

    tn.read_until(b'#')
    tn.write(b'show gpon onu detail-info gpon-onu_' +
             interface.encode('ascii') + b'\n')
    time.sleep(0.1)

    data = tn.read_until(b'#').decode('utf-8')
    return data


def reboot(host, gpon_onu):

    tn = session(host)

    cmd = """
    conf t

    pon-onu-mng gpon-onu_{}

    reboot
    """.format(gpon_onu)

    tn.write(cmd.encode('ascii'))
    time.sleep(0.05)
    tn.read_until(b'Confirm to reboot? [yes/no]:')
    tn.write('yes'.encode('ascii') + b'\n')
    time.sleep(0.05)
    tn.write('end'.encode('ascii') + b'\n')
    time.sleep(0.05)

    data = tn.read_very_eager().decode('utf-8')
    return data


def restore_factory(host, gpon_onu):

    tn = session(host)

    cmd = """
    conf t

    pon-onu-mng gpon-onu_{}

    restore factory
    """.format(gpon_onu)

    tn.write(cmd.encode('ascii'))
    time.sleep(0.05)
    tn.write('end'.encode('ascii') + b'\n')
    time.sleep(0.05)

    data = tn.read_very_eager().decode('utf-8')
    return data


def show_pon_onu_uncfg(host):
    tn = session(host)

    tn.write(b'show pon onu uncfg\n')
    time.sleep(0.1)

    data = tn.read_until(b'#').decode('utf-8')
    return data

def show_gpon_onu_by_sn(host, sn):
    tn = session(host)

    tn.write(b'show gpon onu by sn ' +
             sn.encode('ascii') + b'\n')
    time.sleep(0.1)

    return tn.read_until(b'#').decode('utf-8')


def show_gpon_state_by_interface(host, interface):

    tn = session(host)

    tn.write(b"terminal length 0\n")
    time.sleep(0.05)
    tn.read_until(b'#')

    tn.write(b'show gpon onu state gpon-olt_' +
             interface.encode('ascii') + b'\n')
    # time.sleep(0.2)

    return tn.read_until(b'#').decode('utf-8')


def show_onu_type(host):
    tn = session(host)

    tn.write(b"terminal length 0\n")
    time.sleep(0.1)

    tn.read_until(b'#')
    tn.write(b'show onu-type gpon\n')
    time.sleep(0.2)

    data = tn.read_very_eager().decode('utf-8')
    return data


def show_gpon_onu_profile_vlan(host):

    tn = session(host)

    tn.write(b'show gpon onu profile vlan\n')
    time.sleep(0.1)

    data = tn.read_until(b'#').decode('utf-8')
    return data


def show_gpon_onu_distance(host, interface):

    tn = session(host)

    tn.write(b'show gpon onu distance gpon-onu_' +
             interface.encode('ascii') + b'\n')
    time.sleep(0.05)

    data = tn.read_until(b'#').decode('utf-8')
    return data


def onuadd(host, data):

    tn = session(host)

    cmd = """
    conf t

    interface gpon-olt_{}
    onu {} type {} sn {}
    exit

    interface gpon-onu_{}
    name {}
    description {}
    tcont 1 profile default
    gemport 1 tcont 1
    service-port 1 vport 1 user-vlan 143 vlan 143
    exit

    pon-onu-mng gpon-onu_{}
    service 1 gemport 1 vlan 143
    wan-ip 1 mode pppoe username {} password {} vlan-profile netmedia143 host 1
    exit
    exit

    """.format(data['gpon_olt'], data['onu_index'], data['onu_type'], data['sn'], data['gpon_onu'], data['name'], data['description'], data['gpon_onu'], data['username'], data['password'])

    tn.write(cmd.encode('ascii'))
    time.sleep(2)

    data = tn.read_until(b'ZXAN#').decode('utf-8')
    return data


def delete_onu(host, data):

    tn = session(host)

    cmd = """
    conf t

    interface gpon-olt_{}
    no onu {}
    end

    """.format(data['gpon_olt'], data['onu_index'])

    tn.write(cmd.encode('ascii'))
    time.sleep(2)

    return tn.read_very_eager().decode('utf-8')


def remote_onu(host, data):

    tn = session(host)
    if data['state'] == 'enable':
        cmd = """
        conf t
        pon-onu-mng gpon-onu_{}
        security-mgmt 212 state enable mode forward protocol web
        exit
        exit

        """.format(data['gpon_onu'])
    else:
        cmd = """
        conf t
        pon-onu-mng gpon-onu_{}
        no security-mgmt 212
        exit
        exit

        """.format(data['gpon_onu'])

    tn.write(cmd.encode('ascii'))
    time.sleep(1)

    return tn.read_until(b'ZXAN#').decode('utf-8')
