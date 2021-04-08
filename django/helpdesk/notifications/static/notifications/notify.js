const notify_api_url = "/inbox/notifications/api/unread_list/";
let array_data_menu_count = 0 ;

function add_static_notification(html) {
    let notification = document.createElement('li');
    notification.className = "dropdown-item";
    notification.innerHTML = html;
    document.getElementsByClassName("dropdown-menu-insert")[0].append(notification);
}

function update_notification(){
    sendRequest_xhr("GET", notify_api_url).then(data => {
        array = data['unread_list'];
        unread_count = parseInt(data['unread_count']);
        if (unread_count  != array_data_menu_count){
        array_data_menu_count = unread_count;
        document.getElementsByClassName("live_notify_badge")[0].innerHTML = unread_count;
            for (let i = 0; i < unread_count; i++) {
                el = array[i];
                text ="<p class='small'>"+ el.actor + el.verb + "<a href ='/ticket/" +el.actor_object_id +"' class ='alert-a'> перейти</a>" + "</p>";
                add_static_notification(text)
            }
        }
    }).catch(err => console.log(err))

}
update_notification()
setInterval(update_notification , 10000);