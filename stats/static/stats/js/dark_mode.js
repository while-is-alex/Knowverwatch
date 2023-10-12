document.addEventListener("DOMContentLoaded", function () {
    var modeToggle = document.getElementById("modeToggle");
    var body = document.body;
    var darkMode = body.getAttribute("data-dark-mode") === "true";
    var toggleModeUrl = body.getAttribute("data-toggle-mode-url");

    function setInitialDarkMode() {
        if (darkMode) {
            modeToggle.checked = true;
            body.classList.add("dark-mode");
        } else {
            modeToggle.checked = false;
            body.classList.remove("dark-mode");
        }
    }

    modeToggle.addEventListener("change", function () {
        darkMode = modeToggle.checked;

        // Get the CSRF token from the cookie
        var csrftoken = getCookie('csrftoken');

        fetch(toggleModeUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ dark_mode: darkMode }),
        })
            .then(response => {
                console.log("Raw response:", response);
                return response.json();
            })
            .then(data => {
                if (darkMode) {
                    body.classList.add("dark-mode");
                } else {
                    body.classList.remove("dark-mode");
                }
                console.log(data);
            })
            .catch(error => console.error(error));
    });

    setInitialDarkMode();
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
