from app.raisecom import *
from app.dlink import *
from app.cisco import *
from app.zte import *
from app.settings import *
from flask_rq2 import RQ
import pickle
from datetime import datetime
from app.graph import graphtool
from app.models import *
import time
from paramiko import SSHClient
import paramiko
from scp import SCPClient
import requests
import json
from netmiko import ConnectHandler
import sys
import re

rq = RQ()


@rq.job
def scp_copy(ip, user, password, filename, dst):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port=22, username=user, password=password)
    filename = 'app/configs/'+filename
    scp = SCPClient(ssh.get_transport())
    scp.put(filename, dst)


@rq.job
def get_ports_status(ip, devtype):
    if devtype in ['46']:
        dev = raisecom2128()
    if devtype in ['2', '75', '76', '23']:
        dev = des1228()
    if devtype in ['69', '70']:
        dev = raisecom2624()
    if devtype in ['77']:
        dev = zte2928e()
    dev.connect(acc, ip)
    ports = dev.getintstatus()
    dev.exit()
    return ports


@rq.job
def get_mac_vlan(devtype, ip, vlan):
    if devtype in ['46']:
        dev = raisecom2128()
    if devtype in ['2', '75', '76', '23', '4', '62']:
        dev = des1228()
    if devtype in ['4']:
        dev = olt5504()
    if devtype in ['62']:
        dev = olt5508()
    if devtype in ['77']:
        dev = zte2928e()

    dev.connect(acc, ip)
    mac = dev.getmacbyvlan(vlan)
    return mac


@rq.job
def cisco_check_vlan(ip, vlan, action):
    dev = cisco7301()
    dev.connect(acc, ip)
    dev.fictive_route(vlan, action)


@rq.job
def write_access(data):
    if data['type'] in ['46']:
        dev = raisecom2128()
    if str(data['type']) in ['2', '75', '76', '23']:
        dev = des1228()
    if str(data['type']) in ['77']:
        dev = zte2928e()
    dev.connect(acc, data['ip'])
    dev.createvlan(data['vlan'])
    dev.access(data['port'], data['vlan'])


@rq.job
def write_trunk(data, ip, vlans):
    if data['type'] in ['46']:
        dev = raisecom2128()
    if str(data['type']) in ['2', '75', '76', '23']:
        dev = des1228()
    if str(data['type']) in ['69', '70']:
        dev = raisecom2624()
    if str(data['type']) in ['77']:
        dev = zte2928e()
    if str(data['type']) in ['4']:
        dev = olt5504()
    if str(data['type']) in ['62']:
        dev = olt5508()
    dev.connect(acc, ip)
    for vlan in vlans:
        dev.createvlan(vlan)
        dev.addvlan(vlan, data['ports'])
    dev.exit()
    return ['success', "vlans: {}".format(vlans)]


@rq.job
def update_graph():
    get_ = get()
    graphtool_ = graphtool()
    get_.write_to_mongo()
    site_update = datetime.now()
    System.objects().modify(upsert=True, new=True, siteupdate=site_update)
    graphtool_.create_graph()
    System.objects(siteupdate=site_update).modify(
        upsert=True, new=True, graphupdate=datetime.now())
    save = System.objects.first()
    save.graph.replace(pickle.dumps(graphtool_.g))
    save.save()
    return 'success'


@rq.job
def destroyer(acc):
    acc = Account(*acc)
    con = SSH2()
    exist = True
    result = []
    while exist == True:
        ip = 'shv.loc'
        con.connect(ip)
        con.login(acc)
        con.execute('terminal length 0')
        con.execute("show ip route 192.168.1.20")
        route = con.response.splitlines()
        if route[1] == '% Network not in table':
            con.send('exit')
            exist == False
            break
        if len([x for x in route if 'directly connected' in x]) > 0:
            interface = route[5].split()[-1]
            con.execute('sh run int {}'.format(interface))
            intconf = con.response.splitlines()
            delete = [i for i in intconf if '192.168.1.' in i][0]
            con.execute('conf t')
            con.execute('interface {}'.format(interface))
            con.execute('no {}'.format(delete))
            con.execute('end')
            result.append('interface: {} config: {}'.format(interface, delete))
        else:
            host = route[5].split()[3].replace(',', '')
            con.send('exit')
            ip = host
            print(ip)
            con.connect(ip)
            con.login(acc)
            con.execute('terminal length 0')
            con.execute("show ip route 192.168.1.20")
            route = con.response.splitlines()
            interface = route[5].split()[-1]
            con.execute('sh run int {}'.format(interface))
            intconf = con.response.splitlines()
            delete = [i for i in intconf if '192.168.1.' in i][0]
            con.execute('conf t')
            con.execute('interface {}'.format(interface))
            con.execute('no {}'.format(delete))
            result.append('eliminated router: {} interface: {} config: {}'.format(
                host, interface, delete))

    if len(result) == 0:
        result = ['nothing to destroy']
    return result


class get():

    def get_from_site(self):
        """get from billng then delete old data, update or create new data"""
        s = requests.Session()
        s.post(site_address+'login', data=site_acc)
        self.fromsite = json.loads(s.get(
            site_address+ 'root/map/devicesdata?includeDeleted=false&includeAddresses=true&includePorts=true').text)

    def write_to_mongo(self):
        self.get_from_site()
        mongo = [x.uri for x in Device.objects()]
        billing = [str(x['uri']) for x in self.fromsite]
        [Device.objects(uri=x).delete() for x in mongo if x not in billing]
        for i in self.fromsite:
            if i['uri'] in urialias.keys():
                i['uri'] = urialias[i['uri']]
            Device.objects(devid=int(i['id'])).modify(upsert=True, new=True,
                                                      uri=str(i['uri']), devtype=str(i['scheme']), addr='{} {}'.format(i['addr']['str'], i['addr']['house']),
                                                      ports=i['ports'])

    def getsingledevice(self, devid):
        s = requests.Session()
        s.post(site_address+'login', data=site_acc)
        device = json.loads(s.get(
            site_address+'/root/map/getdevicebyid?id={}'.format(devid)).text)
        return device
