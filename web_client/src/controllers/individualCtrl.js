'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('IndividualCtrl', function($scope, statsService, communicationService, $http, debounce) {
    var vm = this;
    vm.individual = null;
    vm.individualDetails = null;
    vm.loading = true;
    vm.selectedSound = 'output_sound';

    $scope.$watch(function() {
      return statsService.data &&
        statsService.data.generations &&
        statsService.data.generations[statsService.selectedGeneration - 1] &&
        statsService.data.generations[statsService.selectedGeneration - 1]
          .individuals[statsService.selectedIndividualIndex] &&
        statsService.data.generations[statsService.selectedGeneration - 1]
          .individuals[statsService.selectedIndividualIndex].id
    }, debounce(100, function() {
      if (statsService.data && statsService.data.generations && statsService.data.generations[statsService.selectedGeneration - 1]) {
        vm.individual = statsService.data.generations[statsService.selectedGeneration - 1]
          .individuals[statsService.selectedIndividualIndex];
        vm.fetchWholeIndividualRepresentation();
      }
    }));

    vm.fetchWholeIndividualRepresentation = function() {
      vm.loading = true;
      $http.get('/individuals/individual_' + vm.individual.id + '.json').then(function(response) {
        vm.individualDetails = response.data;
        vm.loading = false;
      }, function(response) {
        vm.loading = false;
        vm.individualDetails = null;
      });
    }
  });
