(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('communicationService', function($rootScope) {
      var that = this;

      that.init = function() {
        that.ws = new WebSocket('ws://' + location.hostname + ':1337', 'echo-protocol');

        that.sendMessage = function(message) {
          that.ws.send(message);
        };

        that.ws.addEventListener("message", function(e) {
          var message = JSON.parse(e.data);

          var noOp = false;

          if (message.key === 'stats.json') {
            $rootScope.$emit('stats.json', message.data);
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
