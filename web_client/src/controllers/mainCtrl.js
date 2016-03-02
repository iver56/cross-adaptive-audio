'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('MainCtrl', function($scope, statsService) {
    $scope.statsService = statsService;
  });
