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

    initButtons = function() {
        $("#start").click(function() { webui.onStart(); });
        $("#stop").click(function() { webui.onStop(); })
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