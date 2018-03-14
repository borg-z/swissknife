from Exscript import Host, Account
from Exscript.protocols import Telnet, SSH2
from netaddr import *
import textfsm
from app.raisecom_driver import ROSDriver
driver = ROSDriver()


class raisecom2128():

    def connect(self,acc, ip):
        acc = Account(*acc)
        self.con = Telnet(driver=driver)
        self.con.connect(ip)
        self.con.login(acc)
        self.con.debug = 1


    def config(self):
        self.con.execute('conf t')


    def normal(self):
        self.con.execute('end')

    def createvlan(self, vlan):
        self.config()
        self.con.execute('create vlan {} active'.format(vlan))
        self.normal()

    def getmacbyvlan(self, vlan):
        self.con.execute('show mac-address-table l2-address vlan {}'.format(vlan))
        out = self.con.response
        self.exit()
        fsm = open('app/textFSM/raisecom_sh_mac.template')
        re_mac = textfsm.TextFSM(fsm)
        mac  = re_mac.ParseText(out)
        mac2 = [str(EUI(x[0])) for x in mac]
        return mac2

    def getintstatus(self):
        self.con.execute('sh int port')
        out = self.con.response
        self.exit()
        fsm = open('app/textFSM/raisecom_sh_int_port.template')
        re_ports = textfsm.TextFSM(fsm)
        ports  = re_ports.ParseText(out)
        ports_dict = dict() 
        for x in ports:
            ports_dict[x[0]] = {'admin status':x[1], 'link status':x[2]}
        return ports_dict   


    def access(self, port, vlan):
        self.con.execute('int port {}'.format(str(port)))
        self.con.execute('switchport mode access')
        self.con.execute('switchport access vlan {}'.format(vlan))
        self.exit()

    def addvlan(self, vlan, ports):
        self.config()
        for port in ports:
            if port != 0:
                self.con.execute('int port {}'.format(str(port)))
                self.con.execute('switchport mode trunk')
                self.con.execute('switchport trunk allowed vlan add {}'.format(vlan))
            self.normal()    

    def exit(self):

        self.con.send('exit')



class raisecom2624():
    
    def connect(self,acc, ip):
        acc = Account(*acc)
        self.con = Telnet(driver=driver)
        self.con.connect(ip)
        self.con.login(acc)
        self.con.debug = 1


    def config(self):
        self.con.execute('conf t')


    def normal(self):
        self.con.execute('end')

    def createvlan(self, vlan):
        self.config()
        self.con.execute('create vlan {} active'.format(vlan))
        self.normal()


    def addvlan(self, vlan, ports):
        self.config()
        for port in ports:
            if port != 0:
                self.con.execute('interface gigaethernet 1/1/{}'.format(str(port)))
                self.con.execute('switchport mode trunk')
                self.con.execute('switchport trunk allowed vlan add {}'.format(vlan))
        self.normal()    

    def exit(self):
        self.con.send('exit')


class olt5504():
    
    def connect(self,acc, ip):
        acc = Account(*acc)
        self.con = Telnet(driver=driver)
        self.con.connect(ip)
        self.con.login(acc)
        self.con.debug = 1


    def config(self):
        self.con.execute('conf t')

    def normal(self):
        self.con.execute('end')

    def createvlan(self, vlan):
        self.config()
        self.con.execute('create vlan {} active'.format(vlan))
        self.normal()


    def getmacbyvlan(self, vlan):
        self.con.execute('show mac-address-table l2-address vlan {}'.format(vlan))
        out = self.con.response
        self.exit()
        fsm = open('app/textFSM/raisecom_sh_mac.template')
        re_mac = textfsm.TextFSM(fsm)
        mac  = re_mac.ParseText(out)
        mac2 = [str(EUI(x[0])) for x in mac]
        return mac2

    def addvlan(self, vlan, ports):
        pass  

    def exit(self):

        self.con.send('exit')



class olt5508():
    
    def connect(self,acc, ip):
        acc = Account(*acc)
        self.con = Telnet(driver=driver)
        self.con.connect(ip)
        self.con.login(acc)
        self.con.debug = 1
 
    def getmacbyvlan(self, vlan):
        self.con.execute('show mac-address-table l2-address vlan {}'.format(vlan))
        out = self.con.response
        self.exit()
        fsm = open('app/textFSM/raisecom_sh_mac.template')
        re_mac = textfsm.TextFSM(fsm)
        mac  = re_mac.ParseText(out)
        mac2 = [str(EUI(x[0])) for x in mac]
        return mac2

    def config(self):
        self.con.execute('conf t')

    def normal(self):
        self.con.execute('end')

    def createvlan(self, vlan):
        self.config()
        self.con.execute('create vlan {} active'.format(vlan))
        self.normal()


    def addvlan(self, vlan, ports):
        pass  

    def exit(self):
        self.con.send('exit')
