(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('statsService', function() {
      var that = this;

      that.data = null;
      that.selectedGeneration = null;
      that.numGenerations = null;

      that.setData = function(data) {
        that.numGenerations = data.length;
        that.data = data;
      }
    });
})();
