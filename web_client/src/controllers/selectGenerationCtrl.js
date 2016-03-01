'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('SelectGenerationCtrl', function(statsService) {
    var vm = this;
    vm.statsService = statsService;
  });
