var http = require('http');
var chokidar = require('chokidar');
var util = require('util');
require('console-stamp')(console, '[HH:MM:ss]');
var path = require('path');
var jsonFile = require('jsonfile');
var express = require('express');
var fs = require('fs');


process.on('uncaughtException', function(err) {
  console.log(err);
});

var staticServer = express();
staticServer.use(express.static(path.join(__dirname, '..')));
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

var statsDir = path.join(__dirname, '..', 'stats');

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
  jsonFile.readFile(filePath, function(err, obj) {
    if (err) {
      console.error(err);
    } else {
      var objectToSend = {
        key: key,
        filePath: filePath,
        data: obj
      };
      sendObject(objectToSend, client);
    }
  })
}

function getExperimentFolders() {
  return fs.readdirSync(statsDir).filter(function(file) {
    return fs.statSync(path.join(statsDir, file)).isDirectory() && file.indexOf('test') === -1;
  });
}

chokidar.watch(statsDir, {ignored: /[\/\\]\./}).on('change', function(path, stats) {
  if (path.endsWith('stats.json')) {
    console.log('stats.json changed');
    setTimeout(function() {
      // TODO: only broadcast file to clients that are looking at this specific experiment
      sendFile(path, 'stats.json'); // broadcast to all clients
    }, 500);
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

  var experimentFoldersObj = {
    key: 'experimentFolders',
    data: getExperimentFolders()
  };
  sendObject(experimentFoldersObj, connection);

  // Create event listener
  connection.on('message', function(message) {
    var msgObject = JSON.parse(message.utf8Data);
    console.log(msgObject);
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
