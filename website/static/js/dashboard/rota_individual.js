const ROTAID = document.querySelector("#rota-id").value;


/**
 * Save a venue to the API.
 * */
async function saveAllVenues() {

    // Set up somewhere to store our data
    let postData = [];

    // Get all venues
    let venues = document.querySelectorAll(".venue");

    // Loop over each venue
    for(let venue of venues) {

        // Get the positions for each venue
        let positionData = [];
        let positions = venue.querySelectorAll(".position");
        for (let position of positions) {
            positionData.push({
                role: position.querySelector("[name=role]").value,
                start: position.querySelector("[name=start]").value,
                end: position.querySelector("[name=end]").value,
                notes: position.querySelector("[name=notes]").value,
            });
        }

        // Store positions in the venue
        postData.push({
            name: venue.querySelector("[name=name]").value,
            positions: positionData,
        });
    }

    // API the data
    let response = await fetch(`/api/rotas/${ROTAID}`, {
        method: "PUT",
        body: JSON.stringify(postData),
    });

    // If the API call was successful, update the UI
    if (response.status === 200) {
        venueNode.classList.remove("unsaved");
    }
}


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
 * Create a new position node to be added to the DOM.
 * */
async function createNewPositionNode() {

    let positionNode = document.createElement("div");
    positionNode.classList.add("position");
    positionNode.classList.add("unsaved");

    let roles = document.createElement("select");
    roles.classList.add("input");
    roles.name = "role";
    for(let r of await getAllRoles()) {
        roles.appendChild(r.cloneNode(true));
    }

    let startTime = document.createElement("input");
    startTime.classList.add("input");
    startTime.name = "start";
    startTime.placeholder = "Start time";

    let endTime = document.createElement("input");
    endTime.classList.add("input");
    endTime.name = "end";
    endTime.placeholder = "End time";

    let notes = document.createElement("input");
    notes.classList.add("input");
    notes.name = "notes";
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
    return positionNode;
}


/**
 * Create a new venue position within the given node.
 * Does NOT perform an API request.
 * */
async function createNewVenuePosition(event) {
    let venueNode = event.target.parentElement;
    let positionNode = await createNewPositionNode();
    venueNode.appendChild(positionNode);
}


/**
 * Create a new venue node to be added to the DOM.
 * */
function createNewVenueNode(name = "") {
    let venueItem = document.createElement("div");
    venueItem.classList.add("venue");

    let venueName = document.createElement("input");
    venueName.classList.add("input");
    venueName.name = "name";
    venueName.placeholder = "Venue name";
    venueName.value = name;

    let venuePositions = document.createElement("div");
    venuePositions.classList.add("positions");

    let createPositionButton = document.createElement("button");
    createPositionButton.classList.add("button");
    createPositionButton.classList.add("is-success");
    createPositionButton.textContent = "Create position";
    createPositionButton.onclick = createNewVenuePosition

    let deleteVenueButton = document.createElement("button");
    deleteVenueButton.classList.add("button");
    deleteVenueButton.classList.add("is-danger");
    deleteVenueButton.textContent = "Delete venue";
    deleteVenueButton.onclick = (event) => {
        event.target.parentElement.remove();
    };

    venueItem.appendChild(venueName);
    venueItem.appendChild(venuePositions);
    venueItem.appendChild(createPositionButton);
    venueItem.appendChild(deleteVenueButton);

    return venueItem;
}


function addNewVenueNode() {
    let venueNode = createNewVenueNode();
    let venueList = document.querySelector("#venue-list");
    venueList.appendChild(venueNode);
}


/**
 * Get all of the venues associated with this rota from the API.
 * This will clear and hence populate the venues list.
 * */
async function getAllRotaData() {

    // Get the role list to start with
    await getAllRoles();

    // Get the venues associated with the rota
    const response = await fetch(`/api/rotas/${ROTAID}`);
    const venues = await response.json();

    // Clear the venue list
    const venueList = document.querySelector("#venue-list");
    venueList.innerHTML = "";

    // Go through all of the data in the list
    for (let venue of venues.data) {

        // Create a new venue item
        let venueItem = createNewVenueNode(venue.name);
        venueList.appendChild(venueItem);

        // Add positions of the venue
        if(venue.positions) {
            for (let position of venue.positions) {
                let positionNode = await createNewPositionNode();
                positionNode.querySelector("[name=role]").value = position.role;
                positionNode.querySelector("[name=start]").value = position.start;
                positionNode.querySelector("[name=end]").value = position.end;
                positionNode.querySelector("[name=notes]").value = position.notes;
                venueItem.appendChild(positionNode);
            }
        }
    }
}
