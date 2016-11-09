(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('cubism', Cubism);

  function Cubism() {

    function CubismCtrl($scope, debounce, sampleRate, $rootScope, $element, cubismService) {
      var vm = this;

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

        var numSteps = vm.series.series_normalized[0].length;
        var stepTimeInMs = vm.series.ksmps * 1000 / sampleRate;

        // create context and horizon
        if (cubismService.context === null/*cubismService.numSteps !== numSteps || cubismService.stepTimeInMs !== stepTimeInMs*/) {
          cubismService.stepTimeInMs = stepTimeInMs;
          cubismService.numSteps = numSteps;
          cubismService.context = cubism.context()
            .step(stepTimeInMs)
            .size(numSteps)

            // a hack for making the series start at epoch
            .serverDelay(+new Date())
            .clientDelay(-numSteps * stepTimeInMs)
          ;
        }

        var extent = vm.extent || [-3, 3];

        var horizon = cubismService.context.horizon()
          .extent(extent)
          .format(d3.format('.3f'))
          .colors([].concat(window.colorbrewer.RdBu['6']).reverse())
          ;

        // define metric accessor
        function metricAccessor(idx_key) {
          var idx = idx_key.split('_')[0];
          return cubismService.context.metric(function(start, stop, step, callback) {
            var values;
            if (vm.subtract && vm.subtract.series_normalized) {
              values = [];
              for (var i = 0; i < vm.series.series_normalized[idx].length; i++) {
                var value = vm.series.series_normalized[idx][i] - vm.subtract.series_normalized[idx][i];
                values.push(value);
              }
            } else {
              values = vm.series.series_normalized[idx];
            }
            callback(null, values);
          }, idx);
        }

        var series = [];
        for (var i = 0; i < vm.series.order.length; i++) {
          var key = vm.series.order[i];
          series.push(i + '_' + key);
        }

        horizon.metric(metricAccessor);

        // draw graph

        d3.select(vm.$scrollContainer[0]).select(".cubism-graph").selectAll(".horizon")
          .data(series)
          .enter()
          .append("div")
          .attr("class", "horizon")
          .call(horizon);

        // set rule (a vertical line that updates on hover)
        d3.select(vm.$scrollContainer[0]).select(".cubism-container").append("div")
          .attr("class", "rule")
          .call(cubismService.context.rule());

        // set focus (move numbers to the rule on hover)
        cubismService.context.on("focus", function(i) {
          d3.selectAll(".value")
            .style("right", i == null ? null : cubismService.context.size() - i + 10 + "px");
          d3.selectAll(".title")
            .style("opacity", i > 170 || i == null ? 1 : 0)
        }.throttle(16));

        // set axis
        var axis = cubismService.context.axis();
        axis.focusFormat(d3.time.format('%-M:%S:%L'));
        axis.tickFormat(d3.time.format('%-M:%S'));
        d3.select(vm.$scrollContainer[0]).select(".cubism-graph")
          .append("div").attr("class", "axis").append("g").call(axis);

        cubismService.context.stop();  // shouldn't poll new data as if it's real time
      };
    }

    return {
      restrict: 'E',
      scope: {},
      bindToController: {
        series: '=',
        subtract: '=',
        extent: '='
      },
      templateUrl: 'views/cubism.html',
      controller: CubismCtrl,
      controllerAs: 'cubism'
    };
  }
})();
