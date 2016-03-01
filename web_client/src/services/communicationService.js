(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('communicationService', function(statsService, $rootScope) {
      var that = this;

      that.init = function() {
        that.ws = new WebSocket('ws://localhost:1337', 'echo-protocol');

        that.sendMessage = function(message) {
          that.ws.send(message);
        };

        that.ws.addEventListener("message", function(e) {
          var message = JSON.parse(e.data);

          var noOp = false;

          if (message.key === 'stats.json') {
            statsService.data = message.data;
          } else {
            // no operation
            noOp = true;
          }

          if (!noOp) {
            if (!$rootScope.$$phase) {
              $rootScope.$apply();
            }
          }
        });
      }
    });
})();
