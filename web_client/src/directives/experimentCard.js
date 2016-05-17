(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('experimentCard', ExperimentCard);

  function ExperimentCard() {

    function ExperimentCardCtrl($scope, statsService) {
      var vm = this;

      vm.experimentData = null;
      vm.loading = true;
      vm.statsService = statsService;
      statsService.fetchStats(vm.experimentFolder).then(function(response) {
        vm.experimentData = response.data;
        vm.loading = false;
      }, function(response) {
        vm.loading = false;
      })
    }

    return {
      restrict: 'E',
      scope: {},
      bindToController: {
        experimentFolder: '='
      },
      templateUrl: 'views/experiment-card.html',
      controller: ExperimentCardCtrl,
      controllerAs: 'experimentCard'
    };
  }
})();
