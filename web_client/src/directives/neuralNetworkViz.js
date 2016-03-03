(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('neuralNetworkViz', NeuralNetworkViz);

  function NeuralNetworkViz() {

    function NeuralNetworkVizCtrl($scope) {
      var vm = this;

      vm.sigmaContainer = document.getElementById('sigma-container');
      vm.sigmaInstance = new window.sigma(vm.sigmaContainer);
      vm.sigmaInstance.settings({
        labelSize: 'proportional'
      });

      vm.preProcessGraph = function() {
        for (var i = 0; i < vm.graph.edges.length; i++) {
          var greyValue = (255 - 255 * (Math.tanh(vm.graph.edges[i].weight) * 0.5 + 0.5)) | 0;
          vm.graph.edges[i].color = 'rgb(' + greyValue + ',' + greyValue + ',' + greyValue + ')';
        }
      };

      $scope.$watch(function() {
        return vm.graph;
      }, function() {
        vm.sigmaInstance.graph.clear();
        vm.preProcessGraph();
        vm.sigmaInstance.graph.read(vm.graph);
        vm.sigmaInstance.refresh();
      })
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
