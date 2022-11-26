function getOrdinal(d) {
    if (d > 3 && d < 21) return "th";
    switch (d % 10) {
        case 1: return "st";
        case 2: return "nd";
        case 3: return "rd";
        default: return "th";
    }
}


function getMonthName(d) {
    switch (d) {
        case 1: return "January";
        case 2: return "February";
        case 3: return "March";
        case 4: return "April";
        case 5: return "May";
        case 6: return "June";
        case 7: return "July";
        case 8: return "August";
        case 9: return "September";
        case 10: return "October";
        case 11: return "November";
        case 12: return "December";
    }
    throw "Invalid date";
}


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
    {
        let startOrdinal = getOrdinal(start.getUTCDate());
        let startMonthName = getMonthName(start.getUTCMonth());
        newAvStart.innerHTML = `<b>Start</b>: ${start.getUTCDate()}${startOrdinal} ${startMonthName} ${start.getYear() + 1900}`;
    }
    let newAvEnd = document.createElement("p");
    {
        let endOrdinal = getOrdinal(end.getUTCDate());
        let endMonthName = getMonthName(end.getUTCMonth());
        newAvEnd.innerHTML = `<b>End</b>: ${end.getUTCDate()}${endOrdinal} ${endMonthName} ${end.getYear() + 1900}`;
    }

    newAv.appendChild(newAvId);
    newAv.appendChild(newAvStart);
    newAv.appendChild(newAvEnd);
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

    // AJAX our new role
    let startDateNode = form.querySelector("[name='start']");
    let startDate = startDateNode.valueAsDate;
    let endDateNode = form.querySelector("[name='end']");
    let endDate = endDateNode.valueAsDate;
    let site = await fetch(
        "/api/create_availability",
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
