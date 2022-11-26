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
            method: "get",
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
        let newRole = document.createElement("div");
        newRole.classList.add("role");

        let newRoleId = document.createElement("p");
        newRoleId.innerHTML = `<b>ID</b>: ${r.id}`;
        let newRoleName = document.createElement("p");
        newRoleName.innerHTML = `<b>Name</b>: ${r.name}`;
        let newRoleParent = document.createElement("p");
        if(r.parent) {
            let parent = document.querySelector(`form option[value='${r.parent}']`);
            newRoleParent.innerHTML = `<b>Parent</b>: <i>${parent.textContent}</i>`;
        }
        else {
            newRoleParent.innerHTML = `<b>Parent</b>: (None)`;
        }

        newRole.appendChild(newRoleId);
        newRole.appendChild(newRoleName);
        newRole.appendChild(newRoleParent);
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
    {
        let newRole = document.createElement("div");
        newRole.classList.add("role");

        let newRoleId = document.createElement("p");
        newRoleId.innerHTML = `<b>ID</b>: ${data.id}`;
        let newRoleName = document.createElement("p");
        newRoleName.innerHTML = `<b>Name</b>: ${data.name}`;
        let newRoleParent = document.createElement("p");
        if(data.parent) {
            let parent = roleParentNode.querySelector(`option[value='${data.parent}']`);
            newRoleParent.innerHTML = `<b>Parent</b>: <i>${parent.textContent}</i>`;
        }
        else {
            newRoleParent.innerHTML = `<b>Parent</b>: (None)`;
        }

        newRole.appendChild(newRoleId);
        newRole.appendChild(newRoleName);
        newRole.appendChild(newRoleParent);
        roleListNode.appendChild(newRole);
    }

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
