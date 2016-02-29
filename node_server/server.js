var http = require('http');
var chokidar = require('chokidar');
var util = require('util');
require('console-stamp')(console, '[HH:MM:ss]');
var p = require('path');
var jsonfile = require('jsonfile')

var server = http.createServer(function (request, response) {
});

server.listen(1337, function () {
    console.log((new Date()) + ' Server is listening on port 1337');
});

var WebSocketServer = require('websocket').server;
wsServer = new WebSocketServer({
    httpServer: server
});

var count = 0;
var clients = {};

function broadcastFile(filePath, key) {
    jsonfile.readFile(filePath, function (err, obj) {
        var objectToBroadcast = {
            key: key,
            data: obj
        };
        var objectAsJson = JSON.stringify(objectToBroadcast);
        for (var i in clients) {
            if (clients.hasOwnProperty(i)) {
                clients[i].sendUTF(objectAsJson);
            }
        }
    })
}

// TODO: don't hard code paths, but read them from the settings file
var statsDir = p.join('..', 'stats');
chokidar.watch(statsDir, {ignored: /[\/\\]\./}).on('change', function (path, stats) {
    if (path.endsWith('stats.json')) {
        console.log('stats.json changed');
        broadcastFile(path, 'stats.json')
    }
});

wsServer.on('request', function (r) {
    // Code here to run on connection

    var connection = r.accept('echo-protocol', r.origin);

    // Specific id for this client & increment count
    var id = count++;
    // Store the connection method so we can loop through & contact all clients
    clients[id] = connection;

    console.log((new Date()) + ' Connection accepted [' + id + ']');

    // Create event listener
    connection.on('message', function (msg) {
        console.log(msg);

        broadcastStats();
    });

    connection.on('close', function (reasonCode, description) {
        delete clients[id];
        console.log((new Date()) + ' Peer ' + connection.remoteAddress + ' disconnected.');
    });

});

if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function (suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}
