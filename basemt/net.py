import socket as _s
import getpass as _getpass

def is_port_open(addr, port, timeout=2.0):
    '''Checks if a port is open, with timeout.'''

    try:
        sock = _s.socket(_s.AF_INET, _s.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((addr, port))
        return result==0
    except:
        return False

def get_hostname():
    '''Returns the machine's hostname.'''
    return _s.gethostname()


def get_username():
    '''Returns the current username.'''
    return _getpass.getuser()
