function webui() {
    onPingStart = function() {
        if (!webui.runPing) {
            webui.runPing = true;
            setTimeout(webui.sendPing, 0);
        }
    }

    onPingStop = function() {
        webui.runPing = false;
    }

    parsePingResult = function(result) {
        $('#ping-result').append(webui.pingCount);
        $('#ping-result').append(": ");
        if (result.returncode==0) {
            $('#ping-result').append(result.result);
            $('#ping-result').append("\n");
        } else {
            $('#ping-result').append("error\n");
        }
        $('#ping-result').scrollTop($('#ping-result')[0].scrollHeight);
        webui.pingCount += 1;
        console.log(result);
    }

    sendPing = function() {
        if (webui.runPing) {
            address = $('input[name = ping-address]').val()
            iface = $('input[name = ping-interface]').val()
            $.ajax({
                url: "/ping?ip="+address+"&interface="+iface,
                dataType : 'json',
                type : 'GET',
                success: function(newData) {
                    webui.parsePingResult(newData);
                },
                error: function() {
                    $('#ping-result').append("no response -- website unreachable?\n");
                    $('#ping-result').scrollTop($('#ping-result')[0].scrollHeight); 
                }
            });
            setTimeout(webui.sendPing, 1000);
        }
    }

    // Traceroute

    onTraceStart = function() {
        $('#trace-result').val("running...");
        setTimeout(webui.sendTrace, 0);
    }

    parseTraceResult = function(result) {
        if (result.returncode==0) {
            $('#trace-result').val(result.stdout);
        } else {
            $('#trace-result').val(result.stderr);
        }
        console.log(result);
    }

    sendTrace = function() {
        address = $('input[name = trace-address]').val()
        iface = $('input[name = trace-interface]').val()
        $.ajax({
            url: "/trace?ip="+address+"&interface="+iface,
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                webui.parseTraceResult(newData);
            },
            error: function() {
                $('#trace-result').val("no response -- website unreachable?");
            }
        });
    }

    // Dig

    onDigStart = function() {
        $('#dig-result').val("running...");
        setTimeout(webui.sendDig, 0);
    }

    parseDigResult = function(result) {
        if (result.returncode==0) {
            $('#dig-result').val(result.stdout);
        } else {
            $('#dig-result').val(result.stderr);
        }
        console.log(result);
    }

    sendDig = function() {
        hostname = $('input[name = dig-hostname]').val()
        dnsserver = $('input[name = dig-dnsserver]').val()
        $.ajax({
            url: "/dig?hostname="+hostname+"&dnsserver="+dnsserver,
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                webui.parseDigResult(newData);
            },
            error: function() {
                $('#dig-result').val("no response -- website unreachable?");
            }
        });
    }

    // Ifconfig

    onIfconfigStart = function() {
        $('#ifconfig-result').val("running...");
        setTimeout(webui.sendIfconfig, 0);
    }

    parseIfconfigResult = function(result) {
        if (result.returncode==0) {
            $('#ifconfig-result').val(result.stdout);
        } else {
            $('#ifconfig-result').val(result.stderr);
        }
        console.log(result);
    }

    sendIfconfig = function() {
        iface = $('input[name = ifconfig-interface]').val()
        $.ajax({
            url: "/ifconfig?interface="+iface,
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                webui.parseIfconfigResult(newData);
            },
            error: function() {
                $('#ifconfig-result').val("no response -- website unreachable?");
            }
        });
    }    

    // LTE

    onLTEOn = function() {
        $('#lte-result').val("turning on...");
        setTimeout(function() {webui.sendLTE(1)}, 0);
    }

    onLTEOff = function() {
        $('#lte-result').val("turning off...");
        setTimeout(function() {webui.sendLTE(0)}, 0);
    }    

    parseLTEResult = function(result) {
        if (result.returncode==0) {
            $('#lte-result').val(result.stdout);
        } else {
            $('#lte-result').val(result.stderr);
        }
        console.log(result);
    }

    sendLTE = function(val) {
        $.ajax({
            url: "/lte?value=" + val,
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                webui.parseLTEResult(newData);
            },
            error: function() {
                $('#lte-result').val("no response -- website unreachable?");
            }
        });
    }

    sendUsbPowerCycle = function() {
        $("#lte-result").val("running...");
        $.ajax({
            url: "/usbpowercycle",
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                $("#lte-result").val(newData["stdout"]+newData["stderr"])
                console.log(newData);
            },
            error: function() {
                $('#lte-result').val("no response -- website unreachable?");
            }
        });
    }    

    // navigation

    onOpenTab = function(evt, tabName) {
        // Declare all variables
        var i, tabcontent, tablinks;
      
        // Get all elements with class="tabcontent" and hide them
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
          tabcontent[i].style.display = "none";
        }
      
        // Get all elements with class="tablinks" and remove the class "active"
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
          tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
      
        // Show the current tab, and add an "active" class to the button that opened the tab
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
      }

    // info

    sendInfoRequest = function() {
        $.ajax({
            url: "/info",
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                $('#info-hostname').text(newData["hostname"]);
                $('#info-uptime').text(newData["uptime"]);
                $("#info-edge-mon-agent-service").text(newData["edge_mon_agent_service"]["active"] + "/" + newData["edge_mon_agent_service"]["sub"]);
                console.log(newData);
            },
            error: function() {
                $('#info-hostname').text("no response -- website unreachable?");
            }
        });
        // Keep polling for info. Useful on errors to poll until we get a result.
        // Also useful on success to ensure we're still connected.
        setTimeout(webui.sendInfoRequest, 1000);
    }
    
    // info

    sendSystemCtlRequest = function(command, service) {
        $("#service-result").val("executing...");
        $.ajax({
            url: "/systemctl?command="+command+"&service="+service,
            dataType : 'json',
            type : 'GET',
            success: function(newData) {
                $("#service-result").val(newData["stdout"]+newData["stderr"])
                console.log(newData);
            },
            error: function() {
                $('#info-hostname').text("no response -- website unreachable?");
            }
        });
    }       

    initButtons = function() {
        $("#ping-start").click(function() { webui.onPingStart(); });
        $("#ping-stop").click(function() { webui.onPingStop(); })

        $("#trace-start").click(function() { webui.onTraceStart(); });

        $("#dig-start").click(function() { webui.onDigStart(); });

        $("#ifconfig-start").click(function() { webui.onIfconfigStart(); });

        $("#lte-on").click(function() { webui.onLTEOn(); });
        $("#lte-off").click(function() { webui.onLTEOff(); });
        $("#lte-usb-power-cycle").click(function() { webui.sendUsbPowerCycle(); });

        $("#edge-mon-agent-start").click(function() { webui.sendSystemCtlRequest("start", "edge-mon-agent.service"); });
        $("#edge-mon-agent-stop").click(function() { webui.sendSystemCtlRequest("stop", "edge-mon-agent.service"); });
        $("#edge-mon-agent-restart").click(function() { webui.sendSystemCtlRequest("restart", "edge-mon-agent.service"); });

        $("#nav-ping").click(function(event) { webui.onOpenTab(event, "tab-ping"); })
        $("#nav-traceroute").click(function(event) { webui.onOpenTab(event, "tab-traceroute"); })
        $("#nav-dig").click(function(event) { webui.onOpenTab(event, "tab-dig"); })
        $("#nav-ifconfig").click(function(event) { webui.onOpenTab(event, "tab-ifconfig"); })
        $("#nav-lte").click(function(event) { webui.onOpenTab(event, "tab-lte"); })
        $("#nav-services").click(function(event) { webui.onOpenTab(event, "tab-services"); })

        // default tab
        $("#nav-ping").click();

        // start requesting info
        webui.sendInfoRequest();
    }

    startup = function() {
        this.runPing = false;
        this.pingCount = 0;
        this.initButtons();
   }

   return this;
}

$(document).ready(function(){
    webui = webui();
    webui.startup();
});