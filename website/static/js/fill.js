const AVSTATES = "APU";


function changeButtonValue(event) {
    let index = AVSTATES.indexOf(event.target.value);
    let newLetter = AVSTATES.charAt(index + 1);
    if(newLetter == "") {
        newLetter = AVSTATES.charAt(0);
    }
    event.target.textContent = newLetter;
    event.target.value = newLetter;
}


function generateTable() {
    let table = document.querySelector("table");
    let tbody = document.querySelector("tbody");
    let startDate = new Date(table.dataset.start);
    let endDate = new Date(table.dataset.end);
    let working = new Date(startDate);
    while(working <= endDate) {
        let newRow = document.createElement("tr");
        let th = document.createElement("th");
        th.scope = "row";
        th.textContent = working.toDateString();
        newRow.appendChild(th);

        let td = document.createElement("td");
        let button = document.createElement("button");
        button.classList.add("button")
        button.onclick = changeButtonValue
        button.textContent = "A";
        button.value = "A";
        td.appendChild(button);
        newRow.appendChild(td);

        working.setDate(working.getDate() + 1);
        tbody.appendChild(newRow);
    }
}


async function submitAvailability() {

    // Get the data from the user
    document.querySelector("#submit").classList.add("is-loading");
    let allButtons = document.querySelectorAll("table button");
    let userAvailability = [];
    for(let i of allButtons) {
        userAvailability.push(i.value);
    }

    // Send over to the api
    let site = await fetch(
        window.location.pathname,
        {
            method: "POST",
            body: JSON.stringify(userAvailability)
        }
    );
    let data = await site.json();
    alert(data.message);
    document.querySelector("#submit").classList.remove("is-loading");
}
