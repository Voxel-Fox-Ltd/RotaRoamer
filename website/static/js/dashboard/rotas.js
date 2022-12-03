/**
 * Get all of the availability from the API.
 * This function will also clear and fill the select dropdown.
 * */
async function getAllAvailability() {

    // Clear the dropdown
    let dropdown = document.querySelector("#create-new-rota [name='availability']");
    dropdown.innerHTML = "";

    // Ask the API for non-expired availability sheets
    let response = await fetch("/api/availability");

    // Create option nodes for each item
    let json = await response.json();
    for (let availability of json.data) {
        let option = document.createElement("option");
        option.value = availability.id;
        option.innerText = `${getDateString(availability.start)} - ${getDateString(availability.end)}`;
        dropdown.appendChild(option);
    }
}


/**
 * Create and return a rota node to be displayed on the page.
 * */
function createRotaNode(id, availability, start, end) {

    // Create the rota node
    let rotaNode = document.createElement("div");
    rotaNode.classList.add("rota");

    // Create the rota availability
    let rotaId = document.createElement("p");
    rotaId.innerHTML = `<b>ID</b>: ${id}`;
    let rotaAvailability = document.createElement("p");
    rotaAvailability.innerHTML = `<b>Availability ID</b>: ${availability}`;
    let rotaStart = document.createElement("p");
    rotaStart.innerHTML = `<b>Start</b>: ${getDateString(start)}`;
    let rotaEnd = document.createElement("p");
    rotaEnd.innerHTML = `<b>End</b>: ${getDateString(end)}`;
    let rotaLink = document.createElement("a");
    rotaLink.href = `/dashboard/rotas/${id}`;
    rotaLink.appendChild(document.createTextNode("Manage this rota"));

    // Add the availability and a link to the rota node
    rotaNode.appendChild(rotaId);
    rotaNode.appendChild(rotaAvailability);
    rotaNode.appendChild(rotaStart);
    rotaNode.appendChild(rotaEnd);
    rotaNode.appendChild(rotaLink);

    // Return the rota node
    return rotaNode;
}


/**
 * Get all of the rotas from the API for the given user.
 * This will create rota nodes for the page, clearing the current ones and
 * adding all valid new ones.
 * */
async function getAllRotas() {

    // Clear the current rotas
    let rotaHolder = document.querySelector("#rota-list");
    rotaHolder.innerHTML = "";

    // Ask the API nicely for the rotas
    let response = await fetch("/api/rotas");

    // Check the response is valid
    if (!response.ok) {
        console.error("Failed to get rotas");
        return;
    }

    // Build the rotas on the page
    let json = await response.json();
    for (let rota of json.data) {
        let rotaNode = createRotaNode(rota.id, rota.availability, rota.start, rota.end);
        rotaHolder.appendChild(rotaNode);
    }
}


/**
 * Create a new rota from the form data.
 * */
async function createNewRota() {

    // See what availability the user selected
    let availability = document.querySelector("#create-new-rota [name='availability']").value;

    // Create a new rota
    let response = await fetch("/api/rotas", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            availability: availability,
        }),
    });

    // Check the response is valid
    if (!response.ok) {
        let json = await response.json();
        if(json.message) {
            alert(json.message);
        }
        console.error("Failed to create rota");
        return;
    }

    // Update the rotas
    getAllRotas();
}
