'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('SelectIndividualCtrl', function($scope, statsService) {
    var vm = this;
    vm.statsService = statsService;
  });
