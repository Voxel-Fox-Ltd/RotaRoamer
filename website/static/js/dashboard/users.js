const uuid = () =>
  ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
    (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)
  );


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
    // let site = await fetch(
    //     "/api/create_role",
    //     {
    //         method: "POST",
    //         body: JSON.stringify({
    //             name: roleName,
    //             parent: roleParent,
    //         }),
    //     },
    // );
    // let data = await site.json();
    let data = {
        id: uuid(),
        name: roleName,
        parent: roleParent || null,
    };

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
