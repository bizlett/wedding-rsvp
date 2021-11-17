// Original code from Roy Tutorials - https://roytuts.com/python-flask-multi-step-registration-form-with-mysql-jquery/

function validate() {
    var output = true;
    $(".rsvp-signup-error").html('');

    if ($("#account-details").css('display') != 'none') {
        if (!($("#username").val())) {
            output = false;
            $("#username-error").html("Userame required!");
        }

        if (!($("#email").val())) {
            output = false;
            $("#email-error").html("Email required!");
        }

        if (!$("#email").val().match(/^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/)) {
            $("#email-error").html("Invalid Email!");
            output = false;
        }

        if (!($("#user-password").val())) {
            output = false;
            $("#password-error").html("Password required!");
        }

        if (!($("#confirm-password").val())) {
            output = false;
            $("#confirm-password-error").html("Confirm password required!");
        }

        if ($("#user-password").val() != $("#confirm-password").val()) {
            output = false;
            $("#confirm-password-error").html("Password not matched!");
        }
        
    }

    if ($("#guest-details").css('display') != 'none') {
        if (!($("#guest-name").val())) {
            output = false;
            $("#guest-name-error").html("Guest name required!");
        }

        

        if (!($("#address").val())) {
            output = false;
            $("#address-error").html("Address required!");
        }
    }

    return output;
}

$(document).ready(function () {
    $("#next").click(function () {
        var output = validate();
        if (output === true) {
            var current = $(".active");
            var next = $(".active").next("li");
            if (next.length > 0) {
                $("#" + current.attr("id") + "-field").hide();
                $("#" + next.attr("id") + "-field").show();
                $("#back").show();
                $("#finish").hide();
                $(".active").removeClass("active");
                next.addClass("active");
                if ($(".active").attr("id") == $("li").last().attr("id")) {
                    $("#next").hide();
                    $("#finish").show();
                }
            }
        }
    });


    $("#back").click(function () {
        var current = $(".active");
        var prev = $(".active").prev("li");
        if (prev.length > 0) {
            $("#" + current.attr("id") + "-field").hide();
            $("#" + prev.attr("id") + "-field").show();
            $("#next").show();
            $("#finish").hide();
            $(".active").removeClass("active");
            prev.addClass("active");
            if ($(".active").attr("id") == $("li").first().attr("id")) {
                $("#back").hide();
            }
        }
    });

    $("input#finish").click(function (e) {
        var output = validate();
        var current = $(".active");

        if (output === true) {
            return true;
        } else {
            //prevent refresh
            e.preventDefault();
            $("#" + current.attr("id") + "-field").show();
            $("#back").show();
            $("#finish").show();
        }
    });
});