/**
 * Set the default dates (the nearest Monday and related Sunday) into the
 * date picker for creating a new availability.
 * */
function setDefaultDates() {
    let form = document.querySelector("#create-new-availability");
    let date = new Date();
    let endDate = new Date();
    {
        date.setHours(0);
        date.setMinutes(0);
        date.setSeconds(0);
        date.setMilliseconds(0);
    }
    date.setDate(date.getDate() + 1)
    while(date.getDay() != 1) {
        date.setDate(date.getDate() + 1);
    }
    endDate.setDate(date.getDate() + 6);
    form.querySelector("[name='start']").valueAsDate = date;
    form.querySelector("[name='end']").valueAsDate = endDate;
}


/**
 * Create a new availability node for use in the DOM.
 * */
function createAvailabilityNode(id, start, end) {
    let newAv = document.createElement("div");
    newAv.classList.add("availability");
    newAv.dataset.id = id;

    let newAvId = document.createElement("p");
    newAvId.innerHTML = `<b>ID</b>: ${id}`;
    let newAvStart = document.createElement("p");
    newAvStart.innerHTML = `<b>Start</b>: ${getDateString(start)}`;
    let newAvEnd = document.createElement("p");
    newAvEnd.innerHTML = `<b>End</b>: ${getDateString(end)}`;
    let newAvCheckButton = document.createElement("a");
    newAvCheckButton.href = `/dashboard/availability/${id}`;
    newAvCheckButton.appendChild(document.createTextNode("Check filled availability"));

    newAv.appendChild(newAvId);
    newAv.appendChild(newAvStart);
    newAv.appendChild(newAvEnd);
    newAv.appendChild(newAvCheckButton);
    return newAv;
}


/**
 * Get all of the availabilities under the user's ID via the API;
 * add all of those availabilities to the page, clearing the ones that are currently
 * on the page.
 * */
async function getAllAvailability() {
    let site = await fetch(
        "/api/availability",
        {
            method: "GET",
        },
    );
    let siteData = await site.json();
    let data = siteData.data;

    let availabilityListNode = document.querySelector("#availability-list");
    availabilityListNode.innerHTML = "";
    for(let r of data) {
        let newAv = createAvailabilityNode(r.id, new Date(r.start), new Date(r.end));
        availabilityListNode.appendChild(newAv);
    }
}


async function createNewAvailability() {

    // Set the button to a loading state
    let form = document.querySelector("#create-new-availability");
    let button = form.querySelector("button");
    button.classList.add("is-loading");

    // Make sure the dates aren't too far apart
    let startDateNode = form.querySelector("[name='start']");
    let startDate = startDateNode.valueAsDate;
    let endDateNode = form.querySelector("[name='end']");
    let endDate = endDateNode.valueAsDate;
    if(endDate < startDate) {
        alert("Start date must be before end date.");
        return;
    }
    else if(endDate == startDate) {
        alert("Start and end date cannot be the same.");
        return;
    }
    else if((endDate - startDate) / (1_000 * 60 * 60 * 24) >= 22) {
        alert("End date can be a max of 21 days after the start date.");
        return;  // I don't bother validating this in the API.
    }

    // AJAX our new role
    let site = await fetch(
        "/api/availability",
        {
            method: "POST",
            body: JSON.stringify({
                start: startDate.toISOString(),
                end: endDate.toISOString(),
            }),
        },
    );
    let siteData = await site.json();
    let data = siteData.data;

    // Add new role to list
    let availabilityListNode = document.querySelector("#availability-list");
    let newAv = createAvailabilityNode(r.id, r.start, r.end);
    availabilityListNode.appendChild(newAv);

    // Reset form
    startDateNode.value = "";
    endDateNode.value = "";
    button.classList.remove("is-loading");
}
