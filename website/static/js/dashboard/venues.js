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
        let newVenue = createVenueNode(venue.id, venue.name);
        venueList.appendChild(newVenue);
    }
}


/**
 * Create a new DOM node for a venue, with the given ID and name.
 * */
function createVenueNode(id, name) {

    // Create the new venue node
    let newVenue = document.createElement("div");
    newVenue.classList.add("venue");
    newVenue.dataset.id = id;
    newVenue.dataset.name = name;

    // Create the venue's ID node
    let newVenueId = document.createElement("p");
    newVenueId.innerHTML = `<b>ID</b>: ${id}`;

    // Create the venue's name node
    let newVenueName = document.createElement("p");
    newVenueName.innerHTML = `<b>Name</b>: ${name}`;

    // Create the venue's delete button
    let newDeleteButton = document.createElement("button");
    newDeleteButton.classList.add("button");
    newDeleteButton.classList.add("delete");
    newDeleteButton.value = id;
    newDeleteButton.onclick = deleteVenue;

    // Create the venue's edit button
    let newEditButton = document.createElement("button");
    newEditButton.classList.add("button");
    newEditButton.classList.add("edit");
    newEditButton.value = id;
    newEditButton.onclick = editVenue;

    // Add all of the nodes to the venue node
    newVenue.appendChild(newVenueId);
    newVenue.appendChild(newVenueName);
    newVenue.appendChild(newDeleteButton);
    newVenue.appendChild(newEditButton);
    return newVenue;
}
