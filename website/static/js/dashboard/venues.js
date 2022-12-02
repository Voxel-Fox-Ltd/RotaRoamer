/**
 * The function called when the user clicks the delete button.
 * Ask the user if they want to delete the venue, and if they do,
 * delete it from the API and update the page.
 * */
async function deleteVenue(event) {

    // Get the ID of the venue they want to delete
    let id = event.target.value;

    // Ask if they're sure
    let sure = confirm(`Are you sure you want to delete this venue?`);
    if(!sure) {
        return;
    }

    // Perform the API request
    let response = await fetch(
        `/api/venues?id=${id}`,
        {
            method: "DELETE",
        },
    );
    json = await response.json();

    // If the request not successful, show them the error message
    if(!response.ok) {
        alert(json.message);
        return;
    }

    // Otherwise, update the page
    getAllVenues();
}


/**
 * Run when the user clicks the edit button. This will change the form
 * to be an edit form, and fill it with the venue's current data.
 * */
async function editVenue(event) {

    // Get the form nodes
    let nameNode = document.querySelector("#create-new-venue [name='name']");
    let displayNode = document.querySelector("#create-new-venue [name='display']");
    let idNode = document.querySelector("#create-new-venue [name='id']");

    // Get the venue node
    let venueNode = document.querySelector(`.venue[data-id='${event.target.value}']`);

    // Change the form values
    nameNode.value = venueNode.dataset.name;
    let display = venueNode.dataset.display;
    displayNode.value = display ? display : "";
    idNode.value = venueNode.dataset.id;

    // Hide the venue and unhide other venues
    for(let i of document.querySelectorAll(".venue.hidden")) {
        i.classList.remove("hidden");
    }
    venueNode.classList.add("hidden");

    // Hide the create button and show the edit buttons
    for(let i of document.querySelectorAll("#create-new-venue button[role='create']")) {
        i.classList.add("hidden");
    }
    for(let i of document.querySelectorAll("#create-new-venue button:not([role='create'])")) {
        i.classList.remove("hidden");
    }
}


/**
 * Called when the cancel edit button is pressed on the page.
 * This will clear the form and show the create button again.
 * */
function cancelEditVenue() {

    // Get the form nodes
    let nameNode = document.querySelector("#create-new-venue [name='name']");
    let displayNode = document.querySelector("#create-new-venue [name='display']");
    let idNode = document.querySelector("#create-new-venue [name='id']");

    // Change the form values
    nameNode.value = "";
    displayNode.value = "";
    idNode.value = "";

    // Show all venues
    for(let i of document.querySelectorAll(".venue.hidden")) {
        i.classList.remove("hidden");
    }

    // Hide the edit buttons and show the create button
    for(let i of document.querySelectorAll("#create-new-venue button[role='create']")) {
        i.classList.remove("hidden");
    }
    for(let i of document.querySelectorAll("#create-new-venue button:not([role='create'])")) {
        i.classList.add("hidden");
    }
}


/**
 * Get all of the venues for the associated users, and add them to the page.
 * Running this function clears the current things in the #venue-list DOM node.
 * */
async function getAllVenues() {

    // Clear the current venues
    let venueList = document.querySelector("#venue-list");
    venueList.innerHTML = "";

    // Get all of the venues
    let response = await fetch(
        `/api/venues`,
        {
            method: "GET",
        },
    );
    json = await response.json();
    let venues = json.data;

    // Create a new DOM node for each venue
    for(let venue of venues) {
        let newVenue = createVenueNode(venue.id, venue.name, venue.display);
        venueList.appendChild(newVenue);
    }
}


/**
 * Create a new DOM node for a venue, with the given ID and name.
 * */
function createVenueNode(id, name, display) {

    // Create the new venue node
    let newVenue = document.createElement("div");
    newVenue.classList.add("venue");
    newVenue.dataset.id = id;
    newVenue.dataset.name = name;
    newVenue.dataset.display = display ? display : "";

    // Create the venue's ID node
    let newVenueId = document.createElement("p");
    newVenueId.innerHTML = `<b>ID</b>: ${id}`;

    // Create the venue's name node
    let newVenueName = document.createElement("p");
    newVenueName.innerHTML = `<b>Name</b>: ${name}`;

    // Create the venue's display name node
    let newVenueDisplayName = document.createElement("p");
    newVenueDisplayName.innerHTML = `<b>Display Name</b>: ${display ? display : name}`;

    // Create the venue's delete button
    let newDeleteButton = document.createElement("button");
    newDeleteButton.classList.add("button");
    newDeleteButton.classList.add("is-danger");
    newDeleteButton.appendChild(document.createTextNode("Delete"))
    newDeleteButton.setAttribute("role", "delete");
    newDeleteButton.value = id;
    newDeleteButton.onclick = deleteVenue;

    // Create the venue's edit button
    let newEditButton = document.createElement("button");
    newEditButton.classList.add("button");
    newEditButton.appendChild(document.createTextNode("Edit"))
    newEditButton.setAttribute("role", "edit");
    newEditButton.value = id;
    newEditButton.onclick = editVenue;

    // Add all of the nodes to the venue node
    newVenue.appendChild(newVenueId);
    newVenue.appendChild(newVenueName);
    newVenue.appendChild(newVenueDisplayName);
    newVenue.appendChild(newDeleteButton);
    newVenue.appendChild(newEditButton);
    return newVenue;
}


/**
 * A function to both create a new venue in the API,
 * and to edit the venue if an ID is given.
 * This will also update the page with the new venue.
 * */
async function createNewVenue() {

    // Get the name, ID, and anything else relevant
    let name = document.querySelector("#create-new-venue [name='name']").value;
    let display = document.querySelector("#create-new-venue [name='display']").value;
    let id = document.querySelector("#create-new-venue [name='id']").value;

    // Perform the API request
    let response = await fetch(
        id ? `/api/venues?id=${id}` : `/api/venues`,
        {
            method: id ? "PATCH" : "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: name,
                display: display,
            }),
        },
    );
    json = await response.json();

    // If the request not successful, show them the error message
    if(!response.ok) {
        alert(json.message);
        return;
    }

    // Otherwise, clear the form and update the page
    document.querySelector("#create-new-venue [name='name']").value = "";
    document.querySelector("#create-new-venue [name='display']").value = "";
    document.querySelector("#create-new-venue [name='id']").value = "";
    getAllVenues();
}
