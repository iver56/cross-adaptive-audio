(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('cubism', Cubism);

  function Cubism() {

    function CubismCtrl($scope, debounce, sampleRate, $rootScope, $element) {
      var vm = this;

      // define the order of the series
      vm.sortedSeries = [
        "mfcc_amp",
        "mfcc_1",
        "mfcc_2",
        "mfcc_3",
        "mfcc_4",
        "mfcc_5",
        "mfcc_6",
        "mfcc_7",
        "mfcc_8",
        "mfcc_9",
        "mfcc_10",
        "mfcc_11",
        "mfcc_12"
      ];

      $scope.$watch(function() {
        return vm.series;
      }, debounce(100, function() {
        vm.showGraph();
      }));

      vm.$scrollContainer = $($element[0]).find('.cubism-scroll-container');

      $rootScope.$on('waveform.scroll', function(e, payload) {
        vm.$scrollContainer.scrollLeft(payload.scrollLeft);
      });

      vm.reset = function() {
        // Remove the DOM elements and recreate them. Kinda hacky.
        var $cubismContainer = $('<div class="cubism-container"></div>');
        var $cubismGraph = $('<div class="cubism-graph"></div>');
        $cubismContainer.append($cubismGraph);
        vm.$scrollContainer.empty().append($cubismContainer);
      };

      vm.showGraph = function() {
        vm.reset();

        var stepTimeInMs = vm.series.ksmps * 1000 / sampleRate;
        var numSteps = vm.series.series_standardized['mfcc_amp'].length;

        // create context and horizon
        var context = cubism.context()
          .step(stepTimeInMs)
          .size(numSteps)

          // a hack for making the series start at epoch
          .serverDelay(+new Date())
          .clientDelay(-numSteps * stepTimeInMs)
          ;
        var horizon = context.horizon()
          .extent([-3, 3])
          .format(d3.format('.3f'))
          .colors([].concat(window.colorbrewer.RdBu["6"]).reverse())
          ;

        // define metric accessor
        function metricAccessor(name) {
          return context.metric(function(start, stop, step, callback) {
            var values = vm.series.series_standardized[name];
            callback(null, values);
          }, name);
        }

        var series = [];
        for (var i = 0; i < vm.sortedSeries.length; i++) {
          var key = vm.sortedSeries[i];
          if (vm.series.series_standardized.hasOwnProperty(key)) {
            series.push(key);
          }
        }

        horizon.metric(metricAccessor);

        // draw graph
        d3.select(".cubism-graph").selectAll(".horizon")
          .data(series)
          .enter()
          .append("div")
          .attr("class", "horizon")
          .call(horizon);

        // set rule (a vertical line that updates on hover)
        d3.select(".cubism-container").append("div")
          .attr("class", "rule")
          .call(context.rule());

        // set focus (move numbers to the rule on hover)
        context.on("focus", function(i) {
          d3.selectAll(".value")
            .style("right", i == null ? null : context.size() - i + 10 + "px");
          d3.selectAll(".title")
            .style("opacity", i > 150 || i == null ? 1 : 0)
        }.throttle(16));

        // set axis
        var axis = context.axis();
        axis.focusFormat(d3.time.format('%-M:%S:%L'));
        axis.tickFormat(d3.time.format('%-M:%S'));
        d3.select(".cubism-graph").append("div").attr("class", "axis").append("g").call(axis);

        context.stop();  // shouldn't poll new data as if it's real time
      };
    }

    return {
      restrict: 'E',
      scope: {},
      bindToController: {
        series: '='
      },
      templateUrl: 'views/cubism.html',
      controller: CubismCtrl,
      controllerAs: 'cubism'
    };
  }
})();
