"""
A driver for Raisecom ROS
"""
from __future__ import absolute_import
import re
from Exscript.protocols.exception import InvalidCommandException
from Exscript.protocols.drivers import Driver
from Exscript import  Account

_user_re = [re.compile(r'Login:', re.I)]
_password_re = [re.compile(r'Password:')]
_prompt_re = [re.compile(r'[\r\n][\-\w+\.:/]+(?:\([^\)]+\))?[#>] ?$')]
_error_re = [re.compile(r'%Error'),
             re.compile(r'invalid input', re.I),
             re.compile(r'(?:incomplete|ambiguous) command', re.I),
             re.compile(r'connection timed out', re.I),
             re.compile(r'[^\r\n]+ not found', re.I)]


class ROSDriver(Driver):

    def __init__(self):
        Driver.__init__(self, 'ROS')
        self.user_re = _user_re
        self.password_re = _password_re
        self.prompt_re = _prompt_re
        self.error_re = _error_re

    def check_protocol_for_os(self, string):
        if not string:
            return 0
        if 'Cisco' in string:
            return 80
        return 0

    def check_head_for_os(self, string):
        if 'User Access Verification' in string:
            return 60
        if _tacacs_re.search(string):
            return 50
        if _user_re[0].search(string):
            return 30
        return 0

    def init_terminal(self, conn):
        conn.execute('terminal page-break disable')


    def auto_authorize(self, conn, account, flush, bailout):
        conn.set_timeout(1)
        conn.send('\r') 
        try:
            if conn.waitfor([re.compile(r'[\r\n][\-\w+\.:/]+(?:\([^\)]+\))?[>] ?$')]):
                conn.set_timeout(15) 
                conn.send('enable'+'\r')
                conn.app_authorize(Account('admin', 'pass'))
                conn.app_authorize(Account('admin', 'pass'))
        except:
            pass
        conn.set_timeout(15)
        self.init_terminal(conn)           