var http = require('http');
var chokidar = require('chokidar');
var util = require('util');
require('console-stamp')(console, '[HH:MM:ss]');
var p = require('path');
var jsonfile = require('jsonfile');
var express = require('express');


process.on('uncaughtException', function(err) {
  console.log(err);
});

var staticServer = express();
staticServer.use(express.static(p.join(__dirname, '..', 'web_client')));
var staticServerPort = 8080;
staticServer.listen(staticServerPort, function() {
  console.log('File server is listening on port ' + staticServerPort);
});

var server = http.createServer(function(request, response) {
});
var webSocketServerPort = 1337;
server.listen(webSocketServerPort, function() {
  console.log('WebSocket server is listening on port ' + webSocketServerPort);
});

var WebSocketServer = require('websocket').server;
wsServer = new WebSocketServer({
  httpServer: server
});

var count = 0;
var clients = {};

// TODO: don't hard code paths, but read them from the settings file
var statsDir = p.join(__dirname, '..', 'stats');
var statsFilePath = p.join(statsDir, 'stats.json');

function sendObject(objectToSend, client) {
  var objectAsJson = JSON.stringify(objectToSend);
  if (client) {
    client.sendUTF(objectAsJson);
  } else {
    for (var i in clients) {
      if (clients.hasOwnProperty(i)) {
        clients[i].sendUTF(objectAsJson);
      }
    }
  }
}

function sendFile(filePath, key, client) {
  jsonfile.readFile(filePath, function(err, obj) {
    var objectToSend = {
      key: key,
      data: obj
    };
    sendObject(objectToSend, client);
  })
}

function sendStatsFile(client) {
  sendFile(statsFilePath, 'stats.json', client)
}

chokidar.watch(statsDir, {ignored: /[\/\\]\./}).on('change', function(path, stats) {
  if (path.endsWith('stats.json')) {
    console.log('stats.json changed');
    sendStatsFile(); // broadcast to all clients
  }
});

wsServer.on('request', function(r) {
  // Code here to run on connection

  var connection = r.accept('echo-protocol', r.origin);

  // Specific id for this client & increment count
  var id = count++;
  // Store the connection method so we can loop through & contact all clients
  clients[id] = connection;

  console.log('Connection accepted [' + id + ']');

  sendStatsFile(connection);

  // Create event listener
  connection.on('message', function(msg) {
    console.log(msg);
  });

  connection.on('close', function(reasonCode, description) {
    delete clients[id];
    console.log('Peer ' + connection.remoteAddress + ' disconnected.');
  });

});

if (typeof String.prototype.endsWith !== 'function') {
  String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
  };
}
