import socket as _s
import psutil as _p
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


def get_all_inet4_ipaddresses():
    '''Returns all network INET4 interfaces' IP addresses+submasks.
    Returns
    -------
        retval : dict
            A dictionary of interface_name -> (ip_address, submask)
    '''
    retval1 = _p.net_if_addrs()
    retval2 = {}
    for k, v in retval1.items():
        for e in v:
            if e.family == _s.AF_INET:
                retval2[k] = (e.address, e.netmask)
                break

    return retval2
