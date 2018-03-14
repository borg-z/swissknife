from Exscript import Host, Account
from Exscript.protocols import Telnet, SSH2
from netaddr import *
import textfsm
from Exscript.protocols.drivers import ZteDriver
from app.zte_driver import ZteDriver

driver = ZteDriver()




class zte2928e():

    def connect(self,acc, ip):
        acc = Account(*acc)
        self.con = SSH2(driver = driver)
        self.con.connect(ip)
        self.con.login(acc)


    def createvlan(self, vlan):
        self.con.execute('set vlan {} enable'.format(vlan))

    def getmacbyvlan(self, vlan):
        self.con.send('show mac all-types vlan {}'.format(vlan))
        out = self.more() 
        fsm = open('app/textFSM/raisecom_sh_mac.template')
        re_mac = textfsm.TextFSM(fsm)
        mac  = re_mac.ParseText(out)
        mac2 = [str(EUI(x[0])) for x in mac]
        self.exit()
        return mac2                        

    def getintstatus(self):
        self.con.send('show  port')
        out = self.more().replace('\x08', '').replace('----- more ----- Press Q or Ctrl+C to break -----', '')
        fsm = open('app/textFSM/zte_sh_int_port.template')
        re_ports = textfsm.TextFSM(fsm)
        ports = re_ports.ParseText(out)
        for i in ports:
            if i[2] == '':
                nextelement = ports[ports.index(i)+1]
                i[2] = nextelement[2]
                i[3] = nextelement[3]
                ports.remove(nextelement)
            if i[2] == 'up':
                i[2] = i[3]
            i.remove(i[3])   
        ports_dict = dict()     
        for x in ports:
            ports_dict[x[0]] = {'admin status':x[1], 'link status':x[2]}
        self.exit()
        return ports_dict

 

    def more(self):
        self.con.set_timeout(0) 
        end = True
        while end == True:
            [self.con.send('\r') for x in range(0,100)]
            try:
                if self.con.expect_prompt():
                    end = False
            except:
                pass
        self.con.set_timeout(15)
        return self.con.response        


    def access(self, port, vlan):
        self.con.execute('set vlan {} add port {} untag'.format(vlan, port))
        self.con.execute('set port {} pvid {}'.format(port, vlan))
        self.exit()

    def addvlan(self, vlan, ports):
        for port in ports:
            self.con.execute('set vlan {} add port {} tag'.format(vlan, port))  


    def exit(self):
        self.con.send('exit')
        self.con.send('exit')
