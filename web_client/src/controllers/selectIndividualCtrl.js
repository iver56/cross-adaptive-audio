'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('SelectIndividualCtrl', function($scope, statsService, communicationService, individualService) {
    var vm = this;
    vm.statsService = statsService;
    vm.individualService = individualService;
    vm.individual = null;
    vm.loading = false;

    $scope.$watch(function() {
      return statsService.data &&
        statsService.data[statsService.selectedGeneration - 1] &&
        statsService.data[statsService.selectedGeneration - 1]
          .individuals[statsService.selectedIndividualIndex].id
    }, function() {
      if (statsService.data) {
        vm.individual = statsService.data[statsService.selectedGeneration - 1]
          .individuals[statsService.selectedIndividualIndex];
        vm.fetchWholeIndividualRepresentation();
      }
    });

    vm.fetchWholeIndividualRepresentation = function() {
      var message = JSON.stringify({
        'type': 'getFullIndividualRepresentation',
        'key': vm.individual.id
      });
      communicationService.sendMessage(message);
    }
  });
