import socket

# https://stackoverflow.com/a/28950776
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


ip = get_ip()
port = 8087
services_prefix = "/services/services/services"
verbose_log = True

arcade = "Monkey Business"
paseli = 5730
maintenance_mode = False
