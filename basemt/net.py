import socket as _s
import psutil as _p
import getpass as _getpass
import threading as _t
from time import sleep


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


# ----- port forwarding -----


def _pf_forward(source, destination):
    string = ' '
    while string:
        string = source.recv(4096)
        if string:
            destination.sendall(string)
        else:
            source.shutdown(_s.SHUT_RD)
            destination.shutdown(_s.SHUT_WR)


def _pf_server(listen_config, connect_configs, logger=None):
    try:
        dock_socket = _s.socket(_s.AF_INET, _s.SOCK_STREAM)
        listen_params = listen_config.split(':')
        dock_socket.bind((listen_params[0], int(listen_params[1])))
        dock_socket.listen(5)
        if logger:
            logger.info("Listening at '{}'.".format(listen_config))

        while True:
            client_socket, client_addr = dock_socket.accept()
            if logger:
                logger.info("Client '{}' connected to '{}'.".format(client_addr, listen_config))

            for connect_config in connect_configs:
                try:
                    server_socket = _s.socket(_s.AF_INET, _s.SOCK_STREAM)
                    server_socket.settimeout(10) # listen for 10 seconds before going to the next
                    connect_params = connect_config.split(':')
                    result = server_socket.connect_ex((connect_params[0], int(connect_params[1])))
                    if result != 0:
                        if logger:
                            logger.warning("Forward-connecting '{}' to '{}' returned {} instead of 0.".format(client_addr, connect_config, result))
                        continue
                    if logger:
                        logger.info("Client '{}' forwarded to '{}'.".format(client_addr, connect_config))
                    _t.Thread(target=_pf_forward, args=(client_socket, server_socket)).start()
                    _t.Thread(target=_pf_forward, args=(server_socket, client_socket)).start()
                    break
                except:
                    if logger:
                        logger.warning("Unable to forward '{}' to '{}'. Skipping to next server.".format(client_addr, connect_config))
                    continue
            else:
                if logger:
                    logger.error("Unable to forward to any server for client '{}' connected to '{}'.".format(client_addr, listen_config))
    finally:
        sleep(5)
        _t.Thread(target=_pf_server, args=(listen_config, connect_configs), kwargs={'logger': logger}).start()


def launch_port_forwarder(listen_config, connect_configs, logger=None):
    '''Launchs in other threads a port forwarding service.

    Parameters
    ----------
    listen_config : str
        listening config as an 'addr:port' pair. For example, ':30443', '0.0.0.0:324', 'localhost:345', etc.
    connect_configs : iterable
        list of connecting configs, each of which is an 'addr:port' pair. For example, 'www.foomum.com:443', etc.
    logger : logging.Logger or equivalent
        for logging messages
    '''
    _t.Thread(target=_pf_server, args=(listen_config, connect_configs), kwargs={'logger': logger}).start()
