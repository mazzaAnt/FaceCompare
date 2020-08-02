/*global FaceRecognition _config*/



var FaceRecognition = window.FaceRecognition || {};

(function rideScopeWrapper($) {
    var authToken;

    FaceRecognition.authToken.then(function setAuthToken(token) {
        if (token) {
            authToken = token;
        } else {
            window.location.href = '/signin.html';
        }
    }).catch(function handleTokenError(error) {
        alert(error);
        window.location.href = '/signin.html';
    });



    function requestComparison() {
        $.ajax({
            method: 'POST',
            url: _config.api.invokeUrl + '/simpleapi',
            headers: {
                Authorization: authToken
            },
            data: JSON.stringify({
            }),
            beforeSend: function() { $('#results').text(''); $('#loading').show(); $('#comparison-btn').prop("disabled",true);},
            complete: function() { $('#loading').hide(); $('#comparison-btn').prop("disabled",false); },
            contentType: 'application/json',
            success: completeRequest,
            error: function ajaxError(jqXHR, textStatus, errorThrown) {
                console.error('Error requesting ride: ', textStatus, ', Details: ', errorThrown);
                console.error('Response: ', jqXHR.responseText);
                alert('An error occured when requesting :\n' + jqXHR.responseText);
            }
        });
    }

    function completeRequest(result) {

        console.log('Response received from API: ', result);
        $('#results').text(buildOutput(result))
    }

    // Register click handler for #request button
    $(function onDocReady() {
        $('#comparison-btn').click(handleRequestClick);

        FaceRecognition.authToken.then(function updateAuthMessage(token) {
            if (token) {
                displayUpdate('You are authenticated. Click to see your <a href="#authTokenModal" data-toggle="modal">auth token</a>.');
                $('.authToken').text(token);
            }
        });

        if (!_config.api.invokeUrl) {
            $('#noApiMessage').show();
        }
    });

    function handleRequestClick(event) {
        event.preventDefault();
        requestComparison();
    }

    function displayUpdate(text) {
        $('#updates').append($('<li>' + text + '</li>'));
    }

    function buildOutput(result) {

        imageNames = result.imageNamesList;
        scores = result.comparisons;

        comparisonDictionary = {}
        stringBuilder = ""

        var i;
        for (i = 0; i < scores.length; i++) {
            comparisonDictionary[scores[i][0] + scores[i][1]] = scores[i][2]
        }

        for (w = 0; w < imageNames.length; w++)
        {
            stringBuilder += w.toString() + "    " + imageNames[w] + "\n"
        }
            stringBuilder += "\n\n"

        var w;
        for (w = 0; w < imageNames.length; w++)
        {
            stringBuilder += "     " + w.toString() + "    "
        }
            stringBuilder += "\n\n"

        var x;
        var y;
        for (x = 0; x < imageNames.length; x++) {
            stringBuilder += x.toString() + "    "
            for (y = 0; y < imageNames.length; y++) {
                if(imageNames[x]+imageNames[y] in comparisonDictionary)
                {
                    stringBuilder += comparisonDictionary[imageNames[x]+imageNames[y]].substring(0,5) + "     "
                }
                else
                {
                    stringBuilder += "-----     "
                }

            }
                    stringBuilder += "\n"
        }

        return stringBuilder
    }

}(jQuery));
