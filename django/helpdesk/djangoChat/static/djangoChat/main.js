// (c) Josef.Richter [at] me.com
// the same thing in React.js here: https://codepen.io/josefrichter/pen/OjBEMN?editors=0111

const apiai = axios.create({
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: "X-CSRFTOKEN",
  headers: {
    'Authorization': 'Bearer 546cfca2e8d14b48ace60e1d273fc40a',
    'Content-Type': 'application/json',
  }
})


const app = new Vue({
  delimiters: ["[[", "]]"],
  el: '#chat',
  data: {
    newMessageContent: '',
    messages: [],
    errors: []
    // messages: [{user_id: 1, content:'hey guys'}, {user_id: 2, content:'hey, this is Bob'}, {user_id: 3, content:'Hi, this is Steve'}]
  },
  created: function(){
    // get a sample dummy content from an api
//    this.messages = [{username:"Ivan",actor: "actor", content:'hey guys',date:"11.02.2012"}, {username:"Andrey",actor: "owner", content:'hey, this is Bob',date:"11.02.2012"}, {username:"Andrey",actor: "owner", content:'Hi, this is Steve',date:"11.02.2012"}];
    var self = this;
    this.messages = jsonData;
    let timerId = setInterval(function() {
    apiai.get('/chat/api/update').then(response => (
    response.data.forEach(element => self.messages.push(element))
    ))}, 500);
  },
  methods: {
    addMessage: function() {
      // 'this' refers to 'app'.
        console.log(this.newMessageContent);
      apiai.post('/chat/api/new', {
      "msg":this.newMessageContent,
      })
      .catch(e => {
        alert("Не отправленно");
        console.log(e);
      })
      this.newMessageContent = '';
    }
  }
})