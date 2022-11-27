async function getAllAvailability() {

    // Get the availability dates
    let availabilityId = window.location.pathname.split("/").pop();
    let availabilitySite = await fetch(`/api/availability?id=${availabilityId}`);
    let availabilityData = await availabilitySite.json();
    let availabilityMeta = availabilityData.data[0];
    let startDate = new Date(availabilityMeta.start);
    let endDate = new Date(availabilityMeta.end);

    // For ease, let's make a list of dates to display
    let dates = [];
    let working = startDate;
    while(working <= endDate) {
        dates.push(new Date(working));
        working.setDate(working.getDate() + 1);
    }

    // Add the dates to the table
    let thead = document.querySelector("thead");
    let tr = document.createElement("tr");
    tr.appendChild(document.createElement("td"));
    for(let i of dates) {
        let dateHeader = document.createElement("th");
        dateHeader.scope = "col";
        dateHeader.textContent = i.toDateString();
        tr.appendChild(dateHeader)
    }
    thead.appendChild(tr);

    // Get all of the people and their availability
    availabilitySite = await fetch(`/api/user_availability?id=${availabilityId}`);
    availabilityData = await availabilitySite.json();

    // Add each person to the table
    for(let i of availabilityData.data) {
        let tbody = document.querySelector("tbody");
        let newRow = document.createElement("tr");
        // newRow.dataset.id = i.id;
        let nameCol = document.createElement("th");
        nameCol.scope = "row"
        nameCol.dataset.id = i.person_id;
        nameCol.appendChild(document.createTextNode(i.person_name));
        newRow.appendChild(nameCol)
        for(let r of i.availability) {
            let avCol = document.createElement("td");
            avCol.classList.add("availability-cell")
            avCol.textContent = r;
            avCol.dataset.value = r;
            newRow.appendChild(avCol);
        }
        tbody.appendChild(newRow)
    }
}
