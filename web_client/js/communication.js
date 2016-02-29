var ws = new WebSocket('ws://localhost:1337', 'echo-protocol');

function sendMessage(){
  ws.send('yo');
}

ws.addEventListener("message", function(e) {
  // The data is simply the message that we're sending back
  console.log(e);
  var stats = JSON.parse(e.data);
  console.log(stats);
});
