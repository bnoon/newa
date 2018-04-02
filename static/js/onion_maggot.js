function getOnionMaggot() {
    var req_stn = $("select[name=stn] option:selected").val(),
        accend = $("#dpick").val(),
        params = {type: "onion_maggot", stn: req_stn, accend: accend};	
    $("#righttabs").tabs().tabs("option","active",1);
    $("#second").empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
    $.get("/newaDisease/process_input",params,function(data) {
        $("#loading").fadeOut(500, function() {
            $(this).remove();
        });
        $("#second").html(data);
        produce_onionmaggot_graph();
        $("#forecast").on("click", function() {
            $.get("/newaUtil/getForecastUrl/"+req_stn, function(fcst) { 
                var popup_window = window.open(fcst);
                try {
                    popup_window.focus();
                } catch (e) {
                    alert('Popup windows are blocked. Unblock popup windows to see forecast.');
                }
            });
            return false;
        });
    });
    return false;
}
$(document).ready(function() {
    var triggerClick = true, 
        myDate = new Date(),
        todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
    $("#dpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true }).val(todayDate);
    $("#righttabs").tabs({
        activate: function () {
            var center = map.getCenter();
            google.maps.event.trigger(map, 'resize');
            map.setCenter(center);
        }
    });
    $("form .button").on("click", function () {
        getOnionMaggot();
    });
    stateStationMapList({
        reqval: 'all',
        event_type: 'select_station',
        where: '#station_area'
    });
    $.get('/onion_maggot_info.htm',function(helpdata) {
        $('#third').html(helpdata);
    });
    setupNav(triggerClick);
});