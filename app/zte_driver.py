import re
from Exscript.protocols.drivers.driver import Driver
from Exscript import Account
_user_re = [re.compile(r'user ?name:', re.I), re.compile(r'login', re.I)]
_password_re = [re.compile(r'(?:User )?Password:', re.I)]
_prompt_re = [re.compile(
    r'[\r\n][\-\w+\.\(\)]+(?:\([^\)]+\))?[>#$] ?$|(?:\(y/n\)\[n\])'),
    re.compile(r"[\r\n]password: ?", re.I)]  # password prompt to be used in privilege mode when it has
# a password different from the login password.
_error_re = [re.compile(r'%Error'),
             re.compile(r'(?:Unrecognized|Incomplete) command', re.I), re.compile(r'Invalid input', re.I)]

_zte_re = re.compile(r"ZTE", re.I)


class ZteDriver(Driver):

    def __init__(self):
        Driver.__init__(self, 'zte')
        self.user_re = _user_re
        self.password_re = _password_re
        self.prompt_re = _prompt_re
        self.error_re = _error_re

    def auto_authorize(self, conn, account, flush, bailout):
        conn.send('enable\r\n')
        conn.app_authorize(Account('admin', 'pass'))
        conn.app_authorize(Account('admin', 'pass'))

    def check_head_for_os(self, string):
        if _zte_re.search(string):
            return 90
        return 0
