/**
 * Create a new role node that can be added to the DOM.
 * */
function createRoleNode(id, name, parentId) {
    let newRole = document.createElement("div");
    newRole.classList.add("role");
    newRole.dataset.id = id;

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

    newRole.appendChild(newRoleId);
    newRole.appendChild(newRoleName);
    newRole.appendChild(newRoleParent);
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
    let selectNode = document.querySelector("select[name='role-parent']");
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
    let roleNameNode = form.querySelector("[name='role-name']");
    let roleName = roleNameNode.value;
    let roleParentNode = form.querySelector("[name='role-parent']");
    let roleParent = roleParentNode.value;
    let site = await fetch(
        "/api/create_role",
        {
            method: "POST",
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
