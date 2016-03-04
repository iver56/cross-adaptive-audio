(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('neuralNetworkViz', NeuralNetworkViz);

  function NeuralNetworkViz() {

    function NeuralNetworkVizCtrl($scope, debounce, colorService) {
      var vm = this;

      vm.sigmaContainer = document.getElementById('sigma-container');
      vm.sigmaInstance = new window.sigma(vm.sigmaContainer);
      vm.sigmaInstance.settings({
        labelSize: 'proportional',
        sideMargin: 0.02
      });

      vm.preProcessGraph = function() {
        for (var i = 0; i < vm.graph.nodes.length; i++) {
          if (vm.graph.nodes[i].type === 'input') {
            vm.graph.nodes[i].color = '#FF4F86';
          } else if (vm.graph.nodes[i].type === 'bias') {
            vm.graph.nodes[i].color = '#60E246';
          } else if (vm.graph.nodes[i].type === 'hidden') {
            vm.graph.nodes[i].color = '#1F77B4';
          } else if (vm.graph.nodes[i].type === 'output') {
            vm.graph.nodes[i].color = '#FF8F54';
          }
          delete vm.graph.nodes[i].type;
        }

        for (var i = 0; i < vm.graph.edges.length; i++) {
          vm.graph.edges[i].color = colorService.getColor(vm.graph.edges[i].weight);
        }
      };

      $scope.$watch(function() {
        return vm.graph;
      }, debounce(100, function() {
        vm.sigmaInstance.graph.clear();
        vm.preProcessGraph();
        vm.sigmaInstance.graph.read(vm.graph);
        vm.sigmaInstance.refresh();
      }))
    }

    return {
      restrict: 'E',
      scope: {},
      bindToController: {
        graph: '='
      },
      templateUrl: 'views/neural-network-viz.html',
      controller: NeuralNetworkVizCtrl,
      controllerAs: 'nnv'
    };
  }
})();
