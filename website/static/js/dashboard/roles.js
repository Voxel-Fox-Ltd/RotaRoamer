function cancelEditRole() {

    // Hide just the user we're editing
    for(let p of document.querySelectorAll(".role.hidden")) {
        p.classList.remove("hidden");
    }

    // Update the insert field
    document.querySelector(`#create-new-role [name='id']`).value = "";
    document.querySelector(`#create-new-role [name='name']`).value = "";
    document.querySelector("#create-new-role [name='parent']").value = "";
    for(let i of document.querySelectorAll(`#create-new-role [role='create']`)) {
        i.classList.remove("hidden");
    }
    for(let i of document.querySelectorAll(`#create-new-role [role]:not([role='create'])`)) {
        i.classList.add("hidden");
    }
}


function editRole(event) {

    // Hide the node
    let roleId = event.target.value;
    for(let p of document.querySelectorAll(".role.hidden")) {
        p.classList.remove("hidden");
    }
    let roleNode = document.querySelector(`.role[data-id='${roleId}']`);
    roleNode.classList.add("hidden");

    // Change the values of the inputs
    document.querySelector("#create-new-role [name='id']").value = roleNode.dataset.id;
    document.querySelector("#create-new-role [name='name']").value = roleNode.dataset.name;
    document.querySelector("#create-new-role [name='parent']").value = roleNode.dataset.parent;
    for(let i of document.querySelectorAll(`#create-new-role [role='create']`)) {
        i.classList.add("hidden");
    }
    for(let i of document.querySelectorAll(`#create-new-role [role]:not([role='create'])`)) {
        i.classList.remove("hidden");
    }
}


async function deleteRole(event) {

    // Confirm
    let c = confirm("Are you sure you want to delete this role?");
    if(!c) return;

    // Get the button that was clicked
    let roleId = event.target.value;
    event.target.classList.add("is-loading");

    // Do the API request
    let site = await fetch(
        `/api/roles?id=${roleId}`,
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
    getAllRoles();
}


/**
 * Create a new role node that can be added to the DOM.
 * */
function createRoleNode(id, name, parentId) {
    let newRole = document.createElement("div");
    newRole.classList.add("role");
    newRole.dataset.id = id;
    newRole.dataset.name = name;
    newRole.dataset.parent = parentId || "";

    let newRoleId = document.createElement("p");
    newRoleId.innerHTML = `<b>ID</b>: ${id}`;
    let newRoleName = document.createElement("p");
    newRoleName.innerHTML = `<b>Name</b>: ${name}`;
    let newRoleParent = document.createElement("p");
    if(parentId != null) {
        let parent = document.querySelector(`form option[value='${parentId}']`);
        if(parent != null) {
            newRoleParent.innerHTML = `<b>Parent</b>: ${parent.textContent}`;
        }
        else {
            newRoleParent.innerHTML = `<b>Parent</b>: (Could not get role name)`;
        }
    }
    else {
        newRoleParent.innerHTML = `<b>Parent</b>: (None)`;
    }
    let newDeleteButton = document.createElement("button")
    newDeleteButton.classList.add("button");
    newDeleteButton.classList.add("is-danger");
    newDeleteButton.textContent = `Delete ${name}`;
    newDeleteButton.setAttribute("role", "delete");
    newDeleteButton.onclick = deleteRole;
    newDeleteButton.value = id;

    let newEditButton = document.createElement("button")
    newEditButton.classList.add("button");
    newEditButton.textContent = `Edit ${name}`;
    newEditButton.setAttribute("role", "edit");
    newEditButton.onclick = editRole;
    newEditButton.value = id;

    newRole.appendChild(newRoleId);
    newRole.appendChild(newRoleName);
    newRole.appendChild(newRoleParent);
    newRole.appendChild(newDeleteButton);
    newRole.appendChild(newEditButton);
    return newRole;
}


/**
 * Get all of the roles under the user's ID via the API;
 * add all of those roles to the page, clearing the ones that are currently
 * on the page.
 * */
async function getAllRoles() {

    // Perform the API request
    let site = await fetch(
        "/api/roles",
        {
            method: "GET",
        },
    );
    let siteData = await site.json();
    let data = siteData.data;

    // Set up the new options in the dropdown
    let selectNode = document.querySelector("select[name='parent']");
    selectNode.innerHTML = "";
    let defaultSelectOption = document.createElement("option");
    defaultSelectOption.value = "";
    defaultSelectOption.attributes.default = "";
    defaultSelectOption.appendChild(document.createTextNode("(None)"));
    selectNode.appendChild(defaultSelectOption);
    for(let r of data) {
        let newOption = document.createElement("option");
        newOption.value = r.id;
        newOption.appendChild(document.createTextNode(r.name));
        selectNode.appendChild(newOption);
    }

    // Set up the new options in the role list
    let roleListNode = document.querySelector("#role-list");
    roleListNode.innerHTML = "";
    for(let r of data) {
        let newRole = createRoleNode(r.id, r.name, r.parent);
        roleListNode.appendChild(newRole);
    }
}


async function createNewRole() {

    // Set the button to a loading state
    let form = document.querySelector("#create-new-role");
    let button = form.querySelector("button");
    button.classList.add("is-loading");

    // AJAX our new role
    let roleIdNode = form.querySelector("[name='id']");
    let roleId = roleIdNode.value;
    let roleNameNode = form.querySelector("[name='name']");
    let roleName = roleNameNode.value;
    let roleParentNode = form.querySelector("[name='parent']");
    let roleParent = roleParentNode.value;
    let site = await fetch(
        roleId ? `/api/roles?id=${roleId}` : "/api/roles",
        {
            method: roleId ? "PATCH": "POST",
            body: JSON.stringify({
                name: roleName,
                parent: roleParent,
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

    // Delete role if it exists
    let current = document.querySelector(`.role[data-id='${roleId}']`);
    if(current) current.remove();

    // Add new role to list
    let roleListNode = document.querySelector("#role-list");
    let newRole = createRoleNode(data.id, data.name, data.parent);
    roleListNode.appendChild(newRole);

    // Add new role to parent options
    let newRoleOption = document.createElement("option");
    newRoleOption.value = data.id;
    newRoleOption.appendChild(document.createTextNode(data.name));
    roleParentNode.appendChild(newRoleOption)

    // Reset form
    roleNameNode.value = "";
    for(let i of roleParentNode.querySelectorAll("option")) {
        i.selected = false;
        if(i.attributes.default) {
            i.selected = true;
        }
    }
    roleParentNode.value = "";
    button.classList.remove("is-loading");
}
