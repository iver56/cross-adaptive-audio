'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('SelectIndividualCtrl', function($scope, statsService, communicationService, $http) {
    var vm = this;
    vm.statsService = statsService;
    vm.individual = null;
    vm.individualDetails = null;
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
      vm.loading = true;
      $http.get('/individuals/individual_' + vm.individual.id + '.json').then(function(response) {
        console.log(response);
        vm.individualDetails = response.data;
        vm.loading = false;
      }, function(response) {
        console.error(response);
        vm.loading = false;
      });
    }
  });
