$(document).ready(function() {
    let csrfToken = $('[name=csrfmiddlewaretoken]').val();
    $.ajaxSetup({
        headers: { 'X-CSRFToken': csrfToken }
    });

    function updateHeatButtons(isHeatingEnabled) {
        if (isHeatingEnabled) {
            $('#enable_heat_button').removeClass('normal_button').addClass('enable_button');
            $('#disable_heat_button').removeClass('disable_button').addClass('normal_button');
        } else {
            $('#enable_heat_button').removeClass('enable_button').addClass('normal_button');
            $('#disable_heat_button').removeClass('normal_button').addClass('disable_button');
        }
    }

    function sendHeatState(flag) {
        $.ajax({
            url: '/set-home-heating/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ heat_house: flag }),
            success: function(response) {
                console.log('House warming state switched successfully.')
            },
            error: function(xhr) {
                alert('Request error: ' + xhr.responseText);
            }
        });
    }

    $('#enable_heat_button').click(function() {
        sendHeatState(true);
    });

    $('#disable_heat_button').click(function() {
        sendHeatState(false);
    });


    $('#set_temp_button').click(function() {
        let tempValue = $('#target_temp_input').val();
        let csrfToken = $('[name=csrfmiddlewaretoken]').val();

        $.ajax({
            url: '/set-target-temp/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ target_temp: tempValue }),
            success: function(response) {
                console.log('Success:', response);
            },
            error: function(xhr) {
                alert('Request error: ' + xhr.responseText);
            }
        });
    });

    $('#set_water_temp_button').click(function() {
        let waterTemp = $('#water_temp_input').val();
        $.ajax({
            url: '/set-water-temp/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ water_temp: waterTemp }),
            success: function(response) {
                console.log('Target Water Temperature stored in EEPROM:', response);
            },
            error: function(xhr) {
                alert('Request error: ' + xhr.responseText);
            }
        });
    });

    $('#set_flow_temp_button').click(function() {
        let flowTemp = $('#flow_temp_input').val();
        $.ajax({
            url: '/set-flow-temp/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ flow_temp: flowTemp }),
            success: function(response) {
                console.log('Target Flow Temperature stored in EEPROM:', response);
            },
            error: function(xhr) {
                alert('Request error: ' + xhr.responseText);
            }
        });
    });

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
                $('#target_temperature_id').text(data.target_temperature)
                $('#water_temp_input').text(data.water_temp)
                
                
                updateHeatButtons(data.heat_house);
            },
            error: function(xhr, status, error) {
                console.error("Polling error:", error);
            }
        });
    }

    pollBoilerData();

    setInterval(pollBoilerData, 1000);
});