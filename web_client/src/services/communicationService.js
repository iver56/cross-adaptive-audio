(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('communicationService', function(statsService, $rootScope, individualService) {
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
            statsService.setData(message.data);
          } else if (message.key.indexOf('individual') !== -1) {
            individualService.selectedIndividual = message.data;
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
