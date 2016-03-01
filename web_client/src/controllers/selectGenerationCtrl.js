'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('SelectGenerationCtrl', function($scope, statsService) {
    var vm = this;
    vm.statsService = statsService;
  });
