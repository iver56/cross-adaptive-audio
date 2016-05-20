(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('histogramChart', HistogramChart);

  function HistogramChart() {

    function HistogramChartCtrl($scope, statsService) {
      var vm = this;

      vm.statsService = statsService;

      vm.data = {
        bins: null
      };

      vm.options = {
        series: [
          {
            axis: "y",
            dataset: "bins",
            key: "numOccurrences",
            label: "# individuals",
            color: "#FF8F54",
            type: ['column'],
            id: 'numOccurrences'
          }
        ],
        axes: {
          x: {key: "minValue"},
          y: {max: parseInt(statsService.getPopulationSize()) / 2}
        },
        margin: {
          top: 10,
          right: 30,
          bottom: 20,
          left: 30
        },
        tooltipHook: function(d) {
          if (typeof d === 'undefined') {
            return;
          }
          var rows = d.map(function(s) {
            return {
              label: s.series.label,
              value: s.row.y1,
              color: s.series.color,
              id: s.series.id
            }
          });
          return {
            abscissas: (
              '[' + parseFloat(d[0].row.x).toFixed(3) + " - " +
              parseFloat(d[0].row.x + statsService.histogramOptions.step).toFixed(3) + ']'
            ),
            rows: rows
          };
        },
        zoom: {
          x: true,
          y: false
        },
        pan: {
          x: true,
          y: false
        }
      };

      $scope.$watchGroup([function() {
        return statsService.selectedGeneration
      }, function() {
        return statsService.individualEvaluationMeasure
      }], function() {
        if (statsService.data && statsService.data.generations) {
          vm.data.bins = statsService.getHistogramData();
          vm.options.axes.y.max = parseInt(statsService.getPopulationSize() / 2);
        }
      });
    }

    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'views/histogram-chart.html',
      controller: HistogramChartCtrl,
      controllerAs: 'histogramChart'
    };
  }
})();
