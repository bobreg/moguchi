$(document).ready(function() {
    function pollBoilerData() {
        $.ajax({
            url: '/get-boiler-data/',
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                console.log("Polled data successfully:", data);
                
                $('#temperature_id').text("contex.temperature");
            },
            error: function(xhr, status, error) {
                console.error("Polling error:", error);
            }
        });
    }

    pollBoilerData();

    setInterval(pollBoilerData, 1000);
});