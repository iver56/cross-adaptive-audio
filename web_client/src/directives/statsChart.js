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
            key: "similarity_max",
            label: "Max similarity",
            color: "#FF8F54",
            type: ['line', 'dot'],
            id: 'similarity_max'
          },
          {
            axis: "y",
            dataset: "stats",
            key: "similarity_avg",
            label: "Average similarity",
            color: "#1f77b4",
            type: ['line', 'dot'],
            id: 'similarity_avg'
          },
          {
            axis: "y",
            dataset: "stats",
            key: "similarity_min",
            label: "Min similarity",
            color: "#FF4F86",
            type: ['line', 'dot'],
            id: 'similarity_min'
          },
          {
            axis: "y",
            dataset: "stats",
            key: "similarity_std_dev",
            label: "Standard deviation",
            color: "#60E246",
            type: ['line', 'dot'],
            id: 'similarity_std_dev',
            visible: false
          }
        ],
        axes: {x: {key: "generation"}},
        tooltipHook: function(d) {
          if (typeof d === 'undefined') {
            return;
          }
          var rows = d.map(function(s) {
            return {
              label: s.series.label,
              value: s.row.y1.toPrecision(4),
              color: s.series.color,
              id: s.series.id
            }
          });
          return {
            abscissas: 'Generation ' + d[0].row.x,
            rows: rows
          };
        },
        margin: {
          top: 10,
          right: 35,
          bottom: 20,
          left: 35
        },
        zoom: {
          x: true,
          y: true
        },
        pan: {
          x: true,
          y: true
        }
      };

      $scope.$watch(function() {
        return statsService.data && statsService.data.generations;
      }, function() {
        vm.data.stats = statsService.data.generations;
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
