function btn_click(event) {
    url = event.currentTarget.href
    $.get(url)
        .done(function() {
//            alert("Успешно");
            document.location.reload();
        })
        .fail(function() {
            alert("Действия не удалось");
            document.location.reload();
        })
        .always(function() {});
return false
}

function sound_notif() {
    url = "/static/sound/notificate.mp3"
    var audioAlert = new Audio(url);
    audioAlert.play();
};

function showNotification(top = 0, right = 0, className, html,url_for) {

    let notification = document.createElement('div');
    notification.className = "notification";
    if (className) {
        notification.classList.add(className);
        sound_notif();
    }

    notification.style.top = top + 'px';
    notification.style.right = right + 'px';
    html = '<span class="closebtn" onclick="this.parentElement.remove()">×</span>' +html + "<a href ='/ticket/" +url_for +"' class ='alert-a'> перейти</a>"
    notification.innerHTML = html;
    document.body.append(notification);

//    setTimeout(() => notification.remove(), 6000);
}

function update_notif(){
    sendRequest_xhr("GET", "/inbox/notifications/api/unread_list_push/?max=3").then(data => {
        array = data['unread_list'];
        for (let i = 0; i < parseInt(data['unread_count']); i++) {
            el = array[i];
            text = el.actor + el.verb;
            showNotification(i * 40, 0, "body", text,el.actor_object_id)
        }
    }).catch(err => console.log(err))


}

setTimeout(update_notif,1000);
setInterval(update_notif, 100000);