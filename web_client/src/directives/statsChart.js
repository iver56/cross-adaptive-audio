(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('statsChart', StatsChart);

  function StatsChart() {

    function StatsChartCtrl($scope, statsService) {
      var vm = this;

      vm.statsService = statsService;

      vm.data = {
        stats: null
      };

      vm.options = {
        series: [
          {
            axis: "y",
            dataset: "stats",
            key: "fitness_max",
            label: "Max fitness",
            color: "#FF8F54",
            type: ['line', 'dot'],
            id: 'fitness_max'
          },
          {
            axis: "y",
            dataset: "stats",
            key: "fitness_avg",
            label: "Average fitness",
            color: "#1f77b4",
            type: ['line', 'dot'],
            id: 'fitness_avg'
          },
          {
            axis: "y",
            dataset: "stats",
            key: "fitness_std_dev",
            label: "Standard deviation",
            color: "#60E246",
            type: ['line', 'dot'],
            id: 'fitness_std_dev'
          }
        ],
        axes: {x: {key: "generation"}},
        margin: {
          top: 10,
          right: 30,
          bottom: 20,
          left: 30
        }
      };

      $scope.$watch(function() {
        return statsService.data;
      }, function(data) {
        vm.data.stats = statsService.data;
      });
    }

    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'views/stats-chart.html',
      controller: StatsChartCtrl,
      controllerAs: 'statsChart'
    };
  }
})();
