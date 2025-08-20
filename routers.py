import routeros_api
import os

host = str(os.getenv('ROUTER_HOST'))
port = int(os.getenv('ROUTER_PORT'))
# host = '192.168.50.1'
# port = 8728
# print(host)
# print(port)


def mikrotik():
    conn = routeros_api.RouterOsApiPool(
        host,
        username='flaskendpoint',
        password='.flask!',
        port=port,
        plaintext_login=True
    )

    return conn.get_api()


def ppp_profile():
    api = mikrotik()
    list_ppp_profile = api.get_resource('/ppp/profile/')
    result = list_ppp_profile.get()

    profile = []

    for x in result:
        data = {
            'name': x['name']
        }
        profile.append(data)

    return profile


def add_ppp_secret(username, passw, access_mode, pppprofile):
    try:
        conn = mikrotik()
        secret = conn.get_resource('/ppp/secret/')
        tambah = secret.add(name=username, password=passw,
                            service=access_mode, profile=pppprofile)
        return {'message': 'PPP Secret <' + username + '> added.'}
    except Exception as e:
        return {'message': e}


def del_ppp_secret(username):
    try:
        conn = mikrotik()
        # cari data berdasarkan ppp user
        secret = conn.get_resource('/ppp/secret').get(name=username)
        # hapus ppp user berdasarkan id
        dele = conn.get_resource('/ppp/secret')
        dele.remove(id='{}'.format(secret[0]['id']))

        return {'message': 'PPP Secret <' + secret[0]['name'] + '> removed.','status':True}

    except Exception as e:
        print(e)
        return {'message': e,'status':False}
