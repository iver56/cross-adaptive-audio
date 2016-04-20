(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('cubismService', function() {
      this.context = null;
      this.stepTimeInMs = null;
      this.numSteps = null;
    });
})();
