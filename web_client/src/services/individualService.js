(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('individualService', function() {
      var that = this;

      that.selectedIndividual = null;
    });
})();
