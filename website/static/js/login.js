async function submitLogin() {

    // Get the email and password from the user
    let email = document.querySelector("[name='email']").value;
    let password = document.querySelector("[name='password']").value;

    // Make a POST request to the server
    let response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    // If the response is OK, redirect to the home page
    if (response.ok) {
        window.location.href = "/dashboard";
        return;
    }

    // Otherwise, display the error message
    let json = await response.json();
    if(json.message) alert(json.message);
    else alert("Failed to log you in.");
}


async function submitRegister() {

    // Get the email and password from the user
    let email = document.querySelector("[name='email']").value;
    let password = document.querySelector("[name='password']").value;

    // Make a POST request to the server
    let response = await fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    // If the response is OK, redirect to the home page
    if (response.ok) {
        window.location.href = "/dashboard";
        return;
    }

    // Otherwise, display the error message
    let json = await response.json();
    if(json.message) alert(json.message);
    else alert("Failed to create you an account.");
}
