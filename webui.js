function webui() {
    onStart = function() {
        console.log("onStart");
        if (!webui.runPing) {
            webui.runPing = true;
            setTimeout(webui.sendPing, 1000);
        }
    }

    onStop = function() {
        console.log("onStop");
        webui.runPing = false;
    }

    parsePingResult = function(result) {
        $('#result').append(webui.pingCount);
        $('#result').append(": ");
        if (result.returncode==0) {
            $('#result').append(result.result);
            $('#result').append("\n");
        } else {
            $('#result').append("error\n");
        }
        $('#result').scrollTop($('#result')[0].scrollHeight);
        webui.pingCount += 1;
        console.log(result);
    }

    sendPing = function() {
        if (webui.runPing) {
            address = $('input[name = address]').val()
            $.ajax({
                url: "/ping?ip="+address,
                dataType : 'json',
                type : 'GET',
                success: function(newData) {
                    webui.parsePingResult(newData);
                },
                error: function() {
                    $('#result').append("no response -- website unreachable?\n");
                    $('#result').scrollTop($('#result')[0].scrollHeight); 
                }
            });
            setTimeout(webui.sendPing, 1000);
        }
    }

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

    initButtons = function() {
        $("#start").click(function() { webui.onStart(); });
        $("#stop").click(function() { webui.onStop(); })
        $("#nav-ping").click(function(event) { webui.onOpenTab(event, "tab-ping"); })
        $("#nav-traceroute").click(function(event) { webui.onOpenTab(event, "tab-traceroute"); })
        $("#nav-dig").click(function(event) { webui.onOpenTab(event, "tab-dig"); })
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