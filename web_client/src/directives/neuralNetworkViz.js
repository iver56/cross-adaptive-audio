(function() {
  'use strict';

  window.sigma.prototype.resetZoom = function() {
    var camera = this.cameras[0];
    camera.ratio = 1;
    camera.x = 0;
    camera.y = 0;
    this.refresh();
  };

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
        sideMargin: 0.02,
        mouseWheelEnabled: false,
        labelSizeRatio: 1.2
      });

      vm.showResetZoomButton = function() {
        vm.sigmaContainer.getElementsByClassName('reset-zoom')[0].style.display = 'block';
      };

      vm.resetZoom = function() {
        vm.sigmaInstance.resetZoom();
        vm.sigmaContainer.getElementsByClassName('reset-zoom')[0].style.display = 'none';
      };

      vm.sigmaInstance.bind("doubleClickStage", function() {
        vm.showResetZoomButton();
      });

      vm.sigmaInstance.bind("doubleClickNode", function() {
        vm.showResetZoomButton();
      });

      vm.nodeColors = {
        input: '#FF4F86',
        bias: '#60E246',
        hidden: '#1F77B4',
        output: '#FF8F54'
      };

      vm.preProcessGraph = function() {
        for (var i = 0; i < vm.graph.nodes.length; i++) {
          vm.graph.nodes[i].color = vm.nodeColors[vm.graph.nodes[i].type];
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
