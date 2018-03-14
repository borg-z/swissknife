from Exscript import Host, Account
from Exscript.protocols import Telnet, SSH2
import textfsm





class cisco7301():

    def connect(self,acc, ip):
        acc = Account(*acc)
        self.con = SSH2()
        self.con.connect(ip)
        self.con.login(acc)
        self.con.execute('terminal length 0') 


    def get_int_by_vlan(self, vlan):
        self.con.execute('show ip interface brief') 
        out = self.con.response
        fsm = open('app/textFSM/cisco_ios_show_ip_int_brief.template')
        re_int = textfsm.TextFSM(fsm)
        interfaces  = re_int.ParseText(out)
        interface = [x[0] for x in interfaces if str(vlan) in x[0]]
        return interface

    def config(self):
        self.con.execute('conf t')


    def normal(self):
        self.con.execute('end')                

    def fictive_route(self, vlan, action):
        interface = self.get_int_by_vlan(vlan)[0]
        if action == 'add':
            self.config()
            self.con.execute('ip route 1.1.1.1 255.255.255.255 {}'.format(interface))
            self.normal()
            self.con.execute('ping 1.1.1.1 repeat 15 timeout 1')

        if action == 'del':
            self.config()
            self.con.execute('no ip route 1.1.1.1 255.255.255.255 {}'.format(interface))
            self.normal()           
        self.exit()


    def exit(self):
        self.con.send('exit')





