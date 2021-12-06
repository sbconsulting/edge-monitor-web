from bottle import route, run, static_file, request, subprocess
from ipaddress import ip_address
import datetime
import re
import os
import socket

def validateHostName(s):
    try:
        ip_address(s)
        return True
    except ValueError:
        disallowed = re.compile("[^a-zA-Z\d\-]")
        return all(map(lambda x: len(x) and not disallowed.search(x), s.split(".")))


def validateInterface(s):
    return re.match("^[a-zA-Z0-9-_.]*$", s)


def format_timedelta(td, pattern):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    d = {"d": days, "h": hours, "m": minutes, "s": seconds}
    return pattern.format(**d)


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


@route("/info")
def info():
    uptime = os.times().elapsed
    #uptime = str(datetime.timedelta(seconds=uptime))
    uptime = datetime.timedelta(seconds=uptime)
    uptime = format_timedelta(uptime, "{d} days {h}h {m}m {s}s")

    return {"hostname": socket.gethostname(), "uptime": uptime, "returncode": 0}


run(host='0.0.0.0', port=8087, debug=True)
