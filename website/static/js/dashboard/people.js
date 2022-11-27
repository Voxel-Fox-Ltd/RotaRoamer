async function deletePerson(event) {

    // Confirm
    let c = confirm("Are you sure you want to delete this person?");
    if(!c) return;

    // Get the button that was clicked
    let personId = event.target.value;
    event.target.classList.add("is-loading");

    // Do the API request
    let site = await fetch(
        `/api/people?id=${personId}`,
        {
            method: "DELETE",
        },
    );
    if(!site.ok) {
        let json = await site.json();
        alert(json.message);
        event.target.classList.remove("is-loading");
        return
    }

    // Remove the node
    let personNode = document.querySelector(`.person[data-id='${personId}']`);
    personNode.remove();
}


/**
 * Create a new person node that can be added to the DOM.
 * */
function createPersonNode(id, name, email, roleId) {
    let newPerson = document.createElement("div");
    newPerson.classList.add("person");
    newPerson.dataset.id = id;

    let newPersonId = document.createElement("p");
    newPersonId.innerHTML = `<b>ID</b>: ${id}`;
    let newPersonName = document.createElement("p");
    newPersonName.innerHTML = `<b>Name</b>: ${name}`;
    let newPersonEmail = document.createElement("p");
    newPersonEmail.innerHTML = `<b>Email</b>: ${email}`;
    let newPersonRole = document.createElement("p");
    let role = document.querySelector(`select[name='role'] option[value='${roleId}']`);
    if(role != null) {
        newPersonRole.innerHTML = `<b>Role</b>: ${role.textContent}`;
    }
    else {
        newPersonRole.innerHTML = `<b>Role</b>: (Could not get role name)`;
    }
    let newPersonDeleteButton = document.createElement("button")
    newPersonDeleteButton.classList.add("button");
    newPersonDeleteButton.classList.add("is-danger");
    newPersonDeleteButton.textContent = `Delete ${name}`;
    newPersonDeleteButton.setAttribute("role", "delete");
    newPersonDeleteButton.onclick = deletePerson;
    newPersonDeleteButton.value = id;

    newPerson.appendChild(newPersonId);
    newPerson.appendChild(newPersonName);
    newPerson.appendChild(newPersonEmail);
    newPerson.appendChild(newPersonRole);
    newPerson.appendChild(newPersonDeleteButton);
    return newPerson;
}


/**
 * Get a list of all the roles (as an object) from the API.
 * */
async function getAllRoles() {
    let site = await fetch(
        "/api/roles",
        {
            method: "GET",
        },
    );
    let siteData = await site.json();
    return siteData.data;
}


/**
 * Get all of the people under the user's ID via the API;
 * add all of those people to the page, clearing the ones that are currently
 * on the page.
 * This will also clear and reset the role dropdown selector for creating
 * new people.
 * */
async function getAllPeople() {

    // First, let's sort out the role list
    let roleList = document.querySelector("select[name='role']");
    roleList.innerHTML = "";
    for(let r of await getAllRoles()) {
        let newRole = document.createElement("option");
        newRole.value = r.id;
        newRole.textContent = r.name;
        roleList.appendChild(newRole);
    }

    // Perform the API request to get the users
    let site = await fetch(
        "/api/people",
        {
            method: "GET",
        },
    );
    let siteData = await site.json();
    let data = siteData.data;

    // Set up the new options in the role list
    let personListNode = document.querySelector("#person-list");
    personListNode.innerHTML = "";
    for(let r of data) {
        let newPerson = createPersonNode(r.id, r.name, r.email, r.role);
        personListNode.appendChild(newPerson);
    }
}


async function createNewPerson() {

    // Set the button to a loading state
    let form = document.querySelector("#create-new-person");
    let button = form.querySelector("button");
    button.classList.add("is-loading");

    // AJAX our new person
    let personNameNode = form.querySelector("[name='name']");
    let personName = personNameNode.value;
    let personEmailNode = form.querySelector("[name='email']");
    let personEmail = personEmailNode.value;
    let personRoleNode = form.querySelector("[name='role']");
    let personRole = personRoleNode.value;
    let site = await fetch(
        "/api/people",
        {
            method: "POST",
            body: JSON.stringify({
                name: personName,
                email: personEmail,
                role: personRole,
            }),
        },
    );
    let siteData = await site.json();
    if(!site.ok) {
        button.classList.remove("is-loading");
        alert(siteData.message);
        return;
    }
    let data = siteData.data;

    // Add new role to list
    let newPerson = createPersonNode(data.id, data.name, data.email, data.role);
    let personListNode = document.querySelector("#person-list");
    personListNode.appendChild(newPerson);

    // Reset form
    personNameNode.value = "";
    personEmailNode.value = "";
    button.classList.remove("is-loading");
}
