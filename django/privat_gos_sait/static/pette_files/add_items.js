$( document ).ready(function() {
	$("#btn").click(
		function(){
			sendAjaxForm('result_form', 'cart' , "#btn","test1", '/cart/add/{{post.slug }}/');
			return false;
		}
	);
	$("#btn_dell").click(
		function(){
			sendAjaxForm('result_form', 'cart', "#btn_dell","test2",'/cart/remove/{{post.slug }}/');
			return false;
		}
	);
});

function sendAjaxForm(result_form, ajax_form,id_t, text,url) {
$.ajax({
url: url, //url страницы (action_ajax_form.php)
type: "POST", //метод отправки
dataType: "html", //формат данных
data: $("#"+ajax_form).serialize(), // Сеарилизуем объект
success: function(response) { //Данные отправлены успешно
alert("lol1");
	$(id_t).attr('value',text );
},
error: function(response) { // Данные не отправлены
alert("lol");
}
});
}
