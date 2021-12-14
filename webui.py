#!/usr/bin/env python3

from bottle import route, run, static_file, request, subprocess
from ipaddress import ip_address
import datetime
import re
import socket
import time

def validateHostName(s):
    try:
        ip_address(s)
        return True
    except ValueError:
        disallowed = re.compile("[^a-zA-Z\d\-]")
        return all(map(lambda x: len(x) and not disallowed.search(x), s.split(".")))


def validateInterface(s):
    return re.match("^[a-zA-Z0-9-_.]*$", s)


def validateServiceName(s):
    return re.match("^[a-zA-Z0-9-_.]*$", s)    


def format_timedelta(td, pattern):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    d = {"d": days, "h": hours, "m": minutes, "s": seconds}
    return pattern.format(**d)


def get_service_list():
    args = ["systemctl", "list-units", "--type=service", "--plain", "-a"]
    tr = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = tr.communicate(timeout=1)

    if tr.returncode != 0:
        return (tr.returncode, {})

    services = {}
    for line in stdout.splitlines():
        parts = line.decode("utf-8").split(maxsplit=4)
        if len(parts)!=5:
            continue
        parts = [part.strip() for part in parts]

        services[parts[0]] = {
            "name": parts[0],
            "load": parts[1],
            "active": parts[2],
            "sub": parts[3],
            "description": parts[4]
        }

    return (0, services)


@route("/")
def index():
    return static_file("index.html", root=".")

@route("/webui.js")
def webui_js():
    return static_file("webui.js", root=".")

@route("/webui.css")
def webui_css():
    return static_file("webui.css", root=".")

@route("/ping")
def ping():
    ip = request.query.ip or "127.0.0.1"
    if not validateHostName(ip):
        return {"stdout": "", "stderr": "invalid hostname or ip_address", "returncode": -2}

    iface = request.query.interface or None
    if iface and (not validateInterface(iface)):
        return {"stdout": "", "stderr": "invalid interface", "returncode": -2}

    args = ["ping", "-n", "-c", "1", "-w", "1", ip]
    if iface:
        args.append("-I")
        args.append(iface)

    ping = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = ping.communicate()
    if ping.returncode != 0:
        # Check if it's the packet loss message
        for line in stdout.splitlines():
            if "100% packet loss" in line.decode("utf-8"):
                return {"stdout": stdout, "stderr": stderr, "returncode": 0, "result": "packet loss"}
            elif "Network is unreachable" in line.decode("utf-8"):
                # XXX this might be in stderr, not stdout
                return {"stdout": stdout, "stderr": stderr, "returncode": 0, "result": "network is unreachable"}
        
        # something else went wrong
        return {"stdout": stdout, "stderr": stderr, "returncode": ping.returncode}
    else:
        lines = stdout.splitlines()
        for line in lines:
            line = line.decode("utf-8") 
            if "bytes from" in line:
                return {"stdout": stdout, "stderr": stderr, "returncode": ping.returncode, "result": line}

    # It was a successful response, but without a "bytes from" line. Should not happen.
    return {"stdout": stdout, "stderr": stderr, "returncode": -1}


@route("/trace")
def trace():
    ip = request.query.ip or "127.0.0.1"
    if not validateHostName(ip):
        return {"stdout": "", "stderr": "invalid hostname or ip_address", "returncode": -2}

    iface = request.query.interface or None
    if iface and (not validateInterface(iface)):
        return {"stdout": "", "stderr": "invalid interface", "returncode": -2}        

    args = ["traceroute", ip]
    if iface:
        args.append("-i")
        args.append(iface)
    tr = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = tr.communicate()
    return {"stdout": stdout, "stderr": stderr, "returncode": tr.returncode}


@route("/ifconfig")
def ifconfig():
    iface = request.query.interface or None
    if iface and (not validateInterface(iface)):
        return {"stdout": "", "stderr": "invalid interface", "returncode": -2}        

    args = ["ifconfig"]
    if iface:
        args.append(iface)
    process = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return {"stdout": stdout, "stderr": stderr, "returncode": process.returncode}

@route("/lte")
def lte():
    # resets a Sercomm LTE dongle
    value = request.query.value or "1"
    if value != "1":
        value = "0"
    process = subprocess.Popen(["bash", "-c", "echo \"AT+CFUN=%s\" > /dev/ttyACM0" % value],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return {"stdout": stdout, "stderr": stderr, "returncode": process.returncode}


@route("/usbpowercycle")
def usbpowercycle():
    if (int(subprocess.call("which uhubctl",shell=True)) == 0):
        args = ["/usr/sbin/uhubctl", "-a", "0", "-l", "2"]
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return {"stdout": stdout, "stderr": stderr, "returncode": process.returncode}

        time.sleep(10)

        args = ["/usr/sbin/uhubctl", "-a", "1", "-l", "2"]
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return {"stdout": stdout, "stderr": stderr, "returncode": process.returncode}
    else:
        return {"stdout": "", "stderr": "no uhubctl", "returncode": -2}


@route("/dig")
def dig():
    hostname = request.query.hostname or "www.google.com"
    dnsServer = request.query.dnsserver or None

    if not validateHostName(hostname):
        return {"stdout": "", "stderr": "invalid hostname", "returncode": -2}

    if (dnsServer is not None) and (not validateHostName(dnsServer)):
        return {"stdout": "", "stderr": "invalid dns server", "returncode": -2}        

    args = ["dig", hostname]
    if (dnsServer):
        args.append("@"+dnsServer)

    dig = subprocess.Popen(args,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = dig.communicate()
    return {"stdout": stdout, "stderr": stderr, "returncode": dig.returncode}


@route("/systemctl")
def systemctl():
    service = request.query.service or "edge-mon-agent.service"
    command = request.query.command or "restart"

    if not validateServiceName(service):
        return {"stdout": "", "stderr": "invalid service name", "returncode": -2}

    if command not in ["start", "stop", "restart", "enable", "disable"]:
        return {"stdout": "", "stderr": "invalid command name", "returncode": -2}

    args = ["systemctl", command, service]
    process = subprocess.Popen(args,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return {"stdout": stdout, "stderr": stderr, "returncode": process.returncode}


@route("/info")
def info():
    try:
        uptime = time.clock_gettime(time.CLOCK_BOOTTIME)
        uptime = datetime.timedelta(seconds=uptime)
        uptime = format_timedelta(uptime, "{d} days {h}h {m}m {s}s")
    except:
        uptime = "exception"

    try:
        hostname = socket.gethostname()
    except:
        hostname = "exception"

    try:
        service_list = get_service_list()[1]
        if "edge-mon-agent.service" in service_list:
            edge_mon_agent_service = service_list["edge-mon-agent.service"]
        else:
            edge_mon_agent_service = {"active": "not-present"}
    except:
        edge_mon_agent_service = {"active": "exception"}

    return {"hostname": socket.gethostname(),
            "uptime": uptime,
            "returncode": 0,
            "edge_mon_agent_service": edge_mon_agent_service}


if __name__ == "__main__":
    run(host='0.0.0.0', port=8087, debug=True)
