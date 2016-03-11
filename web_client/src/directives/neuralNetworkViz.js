(function() {
  'use strict';

  window.sigma.prototype.resetZoom = function() {
    var camera = this.cameras[0];
    camera.ratio = 1;
    camera.x = 0;
    camera.y = 0;
    this.refresh();
  };

  window.sigma.classes.graph.addMethod('getNeighbors', function(nodeId) {
    var inNeighbors = this.inNeighborsIndex[nodeId] || {};
    var outNeighbors = this.outNeighborsIndex[nodeId] || {};
    return {inNeighbors: inNeighbors, outNeighbors: outNeighbors, nodesIndex: this.nodesIndex};
  });

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

      vm.tooltipPlugin = window.sigma.plugins.tooltips(vm.sigmaInstance, vm.sigmaInstance.renderers[0], {
        node: {
          show: 'clickNode',
          hide: 'clickStage',
          autoadjust: true,
          cssClass: 'sigma-tooltip md-whiteframe-2dp',
          template: '',
          delay: 300
        }
      });

      function getNeighborsUl (neighborsObj, nodesIndex) {
        var $ul = $('<ul></ul>');
        for (var neighborNodeId in neighborsObj) {
          if (Object.prototype.hasOwnProperty.call(neighborsObj, neighborNodeId)) {
            var neighbour = neighborsObj[neighborNodeId];
            var nodeDetails = nodesIndex[neighborNodeId];
            var edgeKey = Object.keys(neighborsObj[neighborNodeId])[0];
            var edge = neighbour[edgeKey];
            var $li = $(
              '<li>' + nodeDetails.label + ' (weight: <span title="' + edge.weight + '">' + edge.weight.toFixed(2) + '</span>)</li>'
            );
            $ul.append($li);
          }
        }
        return $ul;
      }

      vm.tooltipPlugin.bind('shown', function(e) {
        setTimeout(function() {
          var $tooltip = $(vm.sigmaContainer).find('.sigma-tooltip');
          var graph = vm.sigmaInstance.graph;
          var nodeId = e.data.node.id;
          var neighbors = graph.getNeighbors(nodeId);

          $tooltip.empty();

          var hasNoEdges = true;

          if (!$.isEmptyObject(neighbors.inNeighbors)) {
            $tooltip.append($('<span>Incoming edge(s):</span>'));
            var $inNeighborsUl = getNeighborsUl(neighbors.inNeighbors, neighbors.nodesIndex);
            $tooltip.append($inNeighborsUl);
            hasNoEdges = false;
          }

          if (!$.isEmptyObject(neighbors.outNeighbors)) {
            $tooltip.append($('<span>Outgoing edge(s):</span>'));
            var $outNeighborsUl = getNeighborsUl(neighbors.outNeighbors, neighbors.nodesIndex);
            $tooltip.append($outNeighborsUl);
            hasNoEdges = false;
          }

          if (hasNoEdges) {
            $tooltip.append($('<span>This node has no incoming or outgoing edges</span>'));
          }
        }, 0);
      });

      vm.showResetZoomButton = function() {
        $(vm.sigmaContainer).find('.reset-zoom').fadeIn();
      };

      vm.resetZoom = function() {
        vm.sigmaInstance.resetZoom();
        $(vm.sigmaContainer).find('.reset-zoom').fadeOut();
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
