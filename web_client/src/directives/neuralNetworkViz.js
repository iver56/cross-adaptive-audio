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
        edgeColor: 'default',
        defaultEdgeColor: '#999',
        labelSize: 'proportional'
      });

      $scope.$watch(function() {
        return vm.graph;
      }, function() {
        vm.sigmaInstance.graph.clear();
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
