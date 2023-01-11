var last_message_id = "0";
var mutex = false;

display_new_message = function(id, message, sender, time) {
    if (!mutex && last_message_id != id) {
        mutex = true;
        const messages_div = document.getElementById("messages");

        const message_div = document.createElement("div");
        message_div.setAttribute("id", id);
        message_div.setAttribute("style", "margin: 5px;");

        const message_body = document.createElement("p");
        message_body.textContent = "<" + sender + ">: " + message;
        message_body.setAttribute("style", "width: 88%; float: left;");

        const message_time = document.createElement("p");
        message_time.textContent = time;
        message_time.setAttribute("style", "text-align: right; width: 10%; float: right;");

        message_div.appendChild(message_body);
        message_div.appendChild(message_time);
        messages_div.appendChild(message_div);

        last_message_id = id;
        messages_div.scrollTop = messages_div.scrollHeight;
        mutex = false;
    }
};

document.getElementById("msg").addEventListener('keyup', (event) => {
    if (event.keyCode === 13) {
        let form = new FormData();
        form.append("message", document.getElementById("msg").value);

        fetch(window.location.href, {
            body:   form,
            method: "POST"
        }).then(response => response.json()).then(message => display_new_message(message.id, message.message, message.sender, message.time));

        // clear message input
        document.getElementById("msg").value = "";
    }
});

update_messages = async function(){
    var url = new URL(window.location.href);
    url.searchParams.append("last_message", last_message_id);
    const response = await fetch(url, {
        method: "GET"
    });

    if (response.status == 200) {
        const messages = await response.json();
        const keys = Object.keys(messages);

        for (let message_id of keys) {
            display_new_message(message_id, messages[message_id].message, messages[message_id].sender, messages[message_id].time);
        }
    }

};

update_messages();
setInterval(update_messages, 2000);