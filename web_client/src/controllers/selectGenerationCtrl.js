'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('SelectGenerationCtrl', function($scope, statsService) {
    var vm = this;
    vm.statsService = statsService;

    vm.onKeyUp = function (e) {
      var noOp = false;
      if (e.keyCode === 37) { // left arrow
        if (statsService.selectedGeneration > 1) {
          statsService.selectedGeneration -= 1;
        }
      } else if (e.keyCode === 39) { // right arrow
        if (statsService.selectedGeneration < statsService.numGenerations) {
          statsService.selectedGeneration += 1;
        }
      } else {
        // no operation
        noOp = true;
      }
      if (!noOp) {
        if (!$scope.$$phase) {
          $scope.$apply();
        }
      }
    };

    vm.init = function() {
      window.addEventListener("keyup", vm.onKeyUp, false);
    };
    vm.init();
  });
