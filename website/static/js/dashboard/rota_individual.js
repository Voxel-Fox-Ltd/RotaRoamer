const ROTAID = document.querySelector("#rota-id").value;


/**
 * Perform an API request to get all available roles, returning a list of
 * option nodes.
 * */
async function getAllRoles() {

    // See if we have roles stored already
    let roles = document.querySelector("#roles");
    if(roles.dataset.fetched == "1") {
        return [...roles.querySelectorAll("option")]
    }

    // We don't have roles stored, so fetch them
    let response = await fetch("/api/roles");
    let data = await response.json();
    for(let role of data.data) {
        let option = document.createElement("option");
        option.value = role.id;
        option.textContent = role.name;
        roles.appendChild(option);
    }
    roles.dataset.fetched = "1";
    return [...roles.querySelectorAll("option")]
}


/**
 * Create a new venue position within the given node.
 * Does NOT perform an API request.
 * */
async function createNewVenuePosition(event) {
    let venueNode = document.querySelector(`.venue[data-id='${event.target.value}']`);

    let positionNode = document.createElement("div");
    positionNode.classList.add("position");

    let roles = document.createElement("select");
    roles.classList.add("input");
    for(let r of await getAllRoles()) {
        roles.appendChild(r.cloneNode(true));
    }

    let startTime = document.createElement("input");
    startTime.classList.add("input");
    startTime.placeholder = "Start time";

    let endTime = document.createElement("input");
    endTime.classList.add("input");
    endTime.placeholder = "End time";

    let notes = document.createElement("input");
    notes.classList.add("input");
    notes.placeholder = "Notes";

    let removePositionButton = document.createElement("button");
    removePositionButton.classList.add("button");
    removePositionButton.classList.add("is-danger");
    removePositionButton.textContent = "Remove position";
    removePositionButton.onclick = (event) => {
        event.target.parentElement.remove();
    };

    positionNode.appendChild(roles);
    positionNode.appendChild(startTime);
    positionNode.appendChild(endTime);
    positionNode.appendChild(notes);
    positionNode.appendChild(removePositionButton);
    venueNode.appendChild(positionNode);
}


/**
 * Create a new venue node to be added to the DOM.
 * */
function createNewVenueNode(id, name, index) {
    let venueItem = document.createElement("div");
    venueItem.classList.add("venue");
    venueItem.dataset.id = id;
    venueItem.dataset.index = index;
    venueItem.dataset.name = name;

    let venueName = document.createElement("h2");
    venueName.classList.add("name");
    venueName.textContent = name;

    let venuePositions = document.createElement("div");
    venuePositions.classList.add("positions");

    let createPositionButton = document.createElement("button");
    createPositionButton.classList.add("button");
    createPositionButton.classList.add("is-success");
    createPositionButton.textContent = "Create position";
    createPositionButton.value = id;
    createPositionButton.onclick = createNewVenuePosition

    let savePositionButton = document.createElement("button");
    savePositionButton.classList.add("button");
    savePositionButton.textContent = "Save venue";
    savePositionButton.value = id;
    savePositionButton.onclick = (event) => {console.log(event)};

    venueItem.appendChild(venueName);
    venueItem.appendChild(venuePositions);
    venueItem.appendChild(createPositionButton);
    venueItem.appendChild(savePositionButton);

    return venueItem;
}


/**
 * Get all of the venues associated with this rota from the API.
 * This will clear and hence populate the venues list.
 * */
async function getAllVenues() {

    // Get the venues associated with the rota
    const response = await fetch(`/api/rotas/${ROTAID}/venues`);
    const venues = await response.json();

    // Clear the venue list
    const venueList = document.querySelector("#venue-list");
    venueList.innerHTML = "";

    // Add new venues to the list
    for (let venue of venues.data) {
        let venueItem = createNewVenueNode(venue.id, venue.name, venue.index);
        venueList.appendChild(venueItem);
    }
}
