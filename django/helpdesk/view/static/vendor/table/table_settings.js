var data_t;
$(document).ready(function () {
  $.fn.dataTable.moment('MM.DD.YYYY H:mm');
    var eventFired = function ( type ) {
    alert(type);
    }

  document.querySelectorAll("table").forEach(
    el => {
      var table = $(el).DataTable({
        language: lang,
        dom: 'QBfrtip',
        stateSave: true,
        searchBuilder: true,
        lengthChange: false,
        buttons: {
            name: 'primary',
            buttons: [ {extend:'copy',text:"Копировать в буфер"}, 'csv', {
            extend: 'excelHtml5',
            autoFilter: true,
            sheetName: 'Экспорт данных'
        },'pdf',{
        extend:'print',
        text:"Печать"} ]
        },
        "stateSaveCallback": function (settings, data) {
          id_table = settings.nTable.id;
          data_j = JSON.stringify(data);
          data_t = data;
          // localStorage.setItem(id_table, data_j); if use localstore
          url = "/table/"+String(id_table)+"/create/";
          // Send an Ajax request to the server with the state object
            $.ajax( {
              "url": url,
              "data": data_j,
              "dataType": "json",
              "type": "POST",
              "success": function () {}
            } );
          },
        "stateLoadCallback": function (settings) {
          id_table = settings.nTable.id;
          var data_j;
          url = "/table/"+String(id_table)+"/get/"
          $.ajax( {
            url:url,
            async: false,
            dataType: 'json',
            success: function (json) {
            data_j = json;
            }
        } );
          // data_j = JSON.parse(localStorage.getItem(id_table)) if use localstore
          return data_j;
        }
      });
                      table.searchBuilder.container().prependTo(table.table().container());
});
    });
//const requestURL = 'https://jsonplaceholder.typicode.com/users'

//sendRequest('GET', requestURL)
//  .then(data => console.log(data))
//  .catch(err => console.log(err))
//
//const body = {
//  name: 'Vladilen',
//  age: 26
//}
//
// sendRequest('POST', requestURL, body)
//  .then(data => console.log(data))
//  .catch(err => console.log(err))
