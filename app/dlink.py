import pexpect
import textfsm
from netaddr import *


class des1228():

    def connect(self,acc,ip):
        self.con = pexpect.spawn('telnet {}'.format(ip))
        i = self.con.expect(['UserName:','Username:'])
        if i == 0 or i == 1:
            self.con.sendline(acc[0])
        i = self.con.expect(['PassWord:', 'Password:'])
        if i == 0 or i == 1:
            self.con.sendline(acc[1])
        self.con.expect('#')
        self.con.sendline('disable clipaging')
        self.con.expect('#')
        return self.con

    def access(self, port, vlan):
        self.con.sendline('show vlan port {}'.format(port))
        self.con.expect('#')
        out = self.con.before.decode('utf-8').splitlines()
        for i in out:
            if 'X' in i:
                i = i.split()
                self.con.sendline('config vlan vlanid {} delete {}'.format(i[0], port))
        self.con.sendline('config vlan {} add untagged {}'.format(vlan, port))
        self.exit()

    def getmacbyvlan(self, vlan):
        self.con.sendline('show fdb vlanid {}'.format(vlan))
        self.con.expect('#')
        out = self.con.before
        out = out.decode('utf-8')
        self.exit()
        fsm = open('app/textFSM/dlink_sh_mac.template')
        re_mac = textfsm.TextFSM(fsm)
        mac  = re_mac.ParseText(out)
        mac2 = [str(EUI(x[0])) for x in mac]
        return mac2               

    def getintstatus(self):
        self.con.sendline('show ports')
        self.con.expect('#')
        out = self.con.before
        out = out.decode('utf-8')
        
        fsm = open('app/textFSM/dlink_sh_int_port.template')
        re_ports = textfsm.TextFSM(fsm)
        ports  = re_ports.ParseText(out)
        ports_dict = dict() 
        for x in ports:
            ports_dict[x[0]] = {'admin status':x[1], 'link status':x[2]}
        return ports_dict   



    def createvlan(self, vlan):
        self.con.sendline('create vlan {} tag {}'.format(vlan, vlan))
        self.con.expect('#')


    def addvlan(self, vlan, ports):
        for port in ports:
            if port != 0:
                port = str(port)
                self.con.sendline('config vlan {} add tagged {}'.format(vlan, port))
                self.con.expect('#')


    def exit(self):
        self.con.sendline('save')
        self.con.expect('#')
        self.con.sendline('logout')

