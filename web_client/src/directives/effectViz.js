(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('effectViz', EffectViz);

  function EffectViz() {

    function EffectVizCtrl(debounce, $rootScope, $element, statsService, $scope) {
      var vm = this;

      vm.$container = $($element[0]).find('.effect-viz-container');
      vm.canvas = vm.$container.find('canvas.effect-viz-canvas')[0];
      vm.ctx = vm.canvas.getContext('2d');

      $scope.$watch(function() {
        return vm.individual;
      }, debounce(100, function() {
        if (vm.individual) {
          vm.init();
          vm.draw();
        }
      }));

      /*
       $rootScope.$on('waveform.scroll', function(e, payload) {
       //TODO
       });
       */

      vm.init = function() {
        vm.groups = [{effects: []}];
        vm.effects = [];
        var currentGroupIndex = 0;
        var i, effectName;
        for (i = 0; i < statsService.data.args.effect_names.length - 1; i++) {
          effectName = statsService.data.args.effect_names[i];
          if (effectName === 'new_layer') {
            currentGroupIndex += 1;
            vm.groups.push({effects: []});
          } else {
            var effect = {index: i, name: effectName, parameters: []};
            vm.groups[currentGroupIndex].effects.push(effect);
            vm.effects.push(effect);
          }
        }

        var currentEffectIndex = 0;
        for (i = 0; i < vm.individual.neural_output.order.length; i++) {
          var parameterName = vm.individual.neural_output.order[i];

          if (parameterName.indexOf('softmax_') === 0) {
            currentEffectIndex++;
          } else if (effectName !== 'new_layer') {
            vm.effects[currentEffectIndex].parameters.push({
              name: parameterName,
              index: i
            })
          }
        }
      };

      var rectHeight = 80;
      var parameterWidth = 60;
      var knobRadius = 10;
      vm.draw = function() {
        vm.ctx.translate(10, 10);
        for (var i = 0; i < vm.groups.length; i++) {
          vm.ctx.save();

          var group = vm.groups[i];
          for (var j = 0; j < group.effects.length; j++) {
            var effect = group.effects[j];
            var rectWidth = parameterWidth * effect.parameters.length;
            vm.ctx.strokeRect(0, 0, rectWidth, rectHeight);
            vm.ctx.fillText(effect.name, 5, 13);
            vm.ctx.fillRect(0, 20, rectWidth, 1);

            vm.ctx.save();
            vm.ctx.translate(30, 40);
            vm.ctx.textAlign = 'center';

            for (var k = 0; k < effect.parameters.length; k++) {
              var parameter = effect.parameters[k];
              vm.ctx.fillStyle = 'rgb(210, 210, 210)';
              vm.ctx.beginPath();
              vm.ctx.arc(0, 0, knobRadius, 0, 2 * Math.PI);
              vm.ctx.fill();

              vm.ctx.fillStyle = 'rgb(0, 0, 0)';
              vm.ctx.fillText(
                parameter.name.length > 10 ? parameter.name.substring(0, 10) + '...' : parameter.name,
                0,
                25
              );

              vm.ctx.translate(parameterWidth, 0);
            }

            vm.ctx.restore();
            vm.ctx.translate(rectWidth + 20, 0);
          }

          vm.ctx.restore();
          vm.ctx.translate(0, rectHeight + 30);
        }

      };
    }

    return {
      restrict: 'E',
      scope: {},
      bindToController: {
        individual: '='
      },
      templateUrl: 'views/effect-viz.html',
      controller: EffectVizCtrl,
      controllerAs: 'effectViz'
    };
  }
})();
