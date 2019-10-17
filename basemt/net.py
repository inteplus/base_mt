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
        return result == 0
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


def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(_s.SOL_SOCKET, _s.SO_KEEPALIVE, 1)
    sock.setsockopt(_s.IPPROTO_TCP, _s.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(_s.IPPROTO_TCP, _s.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(_s.IPPROTO_TCP, _s.TCP_KEEPCNT, max_fails)


def set_keepalive_osx(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    sends a keepalive ping once every 3 seconds (interval_sec)
    """
    # scraped from /usr/include, not exported by python's socket module
    TCP_KEEPALIVE = 0x10
    sock.setsockopt(_s.SOL_SOCKET, _s.SO_KEEPALIVE, 1)
    sock.setsockopt(_s.IPPROTO_TCP, TCP_KEEPALIVE, interval_sec)


def _pf_forward(source, destination, close_upon_timeout=False, src_config=None, dst_config=None, logger=None):
    string = ' '
    while string:
        try:
            string = source.recv(1024)
        except _s.timeout as e:
            if logger:
                logger.warn_last_exception()
            if close_upon_timeout:
                if logger:
                    logger.warning(
                        "Shutting down the '{}->{}' stream as the source has timed out.".format(src_config, dst_config))
                destination.shutdown(_s.SHUT_WR)
                source.shutdown(_s.SHUT_RD)
            else:
                if logger:
                    logger.warning(
                        "Closing '{}<->{}' connection as the source has timed out.".format(src_config, dst_config)) 
                destination.shutdown(_s.SHUT_RDWR)
                source.shutdown(_s.SHUT_RDWR)
                destination.close()
                source.close()
            break
        except OSError:
            if logger:
                logger.warn_last_exception()
            destination.shutdown(_s.SHUT_RDWR)
            source.shutdown(_s.SHUT_RDWR)
            destination.close()
            source.close()

        if string:
            destination.sendall(string)
        else:
            source.shutdown(_s.SHUT_RD)
            destination.shutdown(_s.SHUT_WR)


def _pf_server(listen_config, connect_configs, close_upon_timeout=False, logger=None):
    try:
        while True:
            try:
                dock_socket = _s.socket(_s.AF_INET, _s.SOCK_STREAM)
            except OSError:
                if logger:
                    logger.warn_last_exception()
                sleep(5)
                continue

            try:
                listen_params = listen_config.split(':')
                dock_socket.bind((listen_params[0], int(listen_params[1])))
                dock_socket.listen(5)
                break
            except OSError:
                if logger:
                    logger.warn_last_exception()
                dock_socket.close()
                sleep(5)
            
        if logger:
            logger.info("Listening at '{}'.".format(listen_config))

        while True:
            client_socket, client_addr = dock_socket.accept()
            client_socket.settimeout(60)  # let's be patient
            set_keepalive_linux(client_socket)  # and keep it alive
            if logger:
                logger.info("Client '{}' connected to '{}'.".format(
                    client_addr, listen_config))

            for connect_config in connect_configs:
                try:
                    server_socket = _s.socket(_s.AF_INET, _s.SOCK_STREAM)
                    # listen for 10 seconds before going to the next
                    server_socket.settimeout(60)
                    set_keepalive_linux(server_socket)  # and keep it alive
                    connect_params = connect_config.split(':')
                    result = server_socket.connect_ex(
                        (connect_params[0], int(connect_params[1])))
                    if result != 0:
                        if logger:
                            logger.warning("Forward-connecting '{}' to '{}' returned {} instead of 0.".format(
                                client_addr, connect_config, result))
                        continue
                    if logger:
                        logger.info("Client '{}' forwarded to '{}'.".format(
                            client_addr, connect_config))
                    _t.Thread(target=_pf_forward, args=(client_socket, server_socket), kwargs={
                        'close_upon_timeout': close_upon_timeout,
                        'logger': logger,
                        'src_config': listen_config,
                        'dst_config': connect_config}).start()
                    _t.Thread(target=_pf_forward, args=(server_socket, client_socket), kwargs={
                        'close_upon_timeout': close_upon_timeout,
                        'logger': logger,
                        'src_config': connect_config,
                        'dst_config': listen_config}).start()
                    break
                except:
                    if logger:
                        logger.warning("Unable to forward '{}' to '{}'. Skipping to next server.".format(
                            client_addr, connect_config))
                    continue
            else:
                if logger:
                    logger.error("Unable to forward to any server for client '{}' connected to '{}'.".format(
                        client_addr, listen_config))
    finally:
        sleep(60)
        _t.Thread(target=_pf_server, args=(listen_config,
                                           connect_configs), kwargs={'logger': logger}).start()


def launch_port_forwarder(listen_config, connect_configs, close_upon_timeout=False, logger=None):
    '''Launchs in other threads a port forwarding service.

    Parameters
    ----------
    listen_config : str
        listening config as an 'addr:port' pair. For example, ':30443', '0.0.0.0:324', 'localhost:345', etc.
    connect_configs : iterable
        list of connecting configs, each of which is an 'addr:port' pair. For example, 'www.foomum.com:443', etc.
    close_upon_timeout : bool
        whether to close the connection upon timeout or just the timed out stream
    logger : logging.Logger or equivalent
        for logging messages
    '''
    _t.Thread(target=_pf_server, args=(listen_config, connect_configs),
              kwargs={'close_upon_timeout': close_upon_timeout, 'logger': logger}).start()
