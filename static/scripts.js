$(document).ready(function() {
    function pollBoilerData() {
        $.ajax({
            url: '/get-boiler-data/',
            type: 'GET',
            dataType: 'json',
            success: function(data) {                
                $('#temperature_id').text(data.temperature);
                $('#flow_temperature_id').text(data.flow_temperature);
                $('#burner_modulation_id').text(data.burner_modulation);
                $('#burner_state_id').text(data.burner_state);
                $('#heating_circuit_state_id').text(data.heating_circuit_state);
                $('#water_circuit_state_id').text(data.water_circuit_state);
                $('#warm_house_id').text(data.warm_house);
                $('#boiler_accepted_command_id').text(data.boiler_accepted_command);
                $('#boiler_connection_id').text(data.boiler_connection);
                $('#controller_connection_id').text(data.controller_connection);
            },
            error: function(xhr, status, error) {
                console.error("Polling error:", error);
            }
        });
    }

    pollBoilerData();

    setInterval(pollBoilerData, 1000);
});