(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('effectViz', EffectViz);

  function EffectViz() {

    function EffectVizCtrl($rootScope, $element, statsService) {
      var vm = this;

      vm.$container = $($element[0]).find('.effect-viz-container');
      vm.canvas = vm.$container.find('canvas.effect-frame-canvas')[0];
      vm.ctx = vm.canvas.getContext('2d');
      vm.knobCanvas = vm.$container.find('canvas.effect-knob-canvas')[0];
      vm.knobCtx = vm.knobCanvas.getContext('2d');
      vm.width = null;
      vm.height = null;

      var margin = 10;
      var rectHeight = 80;
      var verticalSpaceBetweenGroups = 30;
      var horizontalSpaceBetweenEffects = 20;
      var parameterWidth = 60;
      var knobRadius = 10;
      var knobStartAngle = Math.PI / 2;
      var knobEndAngleRelative = 2 * Math.PI;

      $rootScope.$on('waveform.audioprocess', function(e, payload) {
        vm.drawKnobs(payload);
      }.throttle(10));

      vm.getRectWidth = function(effect) {
        return Math.max(
          vm.ctx.measureText(effect.name).width + 10,
          parameterWidth * effect.parameters.length
        );
      };

      vm.calculateDimensions = function() {
        vm.height = margin + (rectHeight + verticalSpaceBetweenGroups) * vm.groups.length;

        var maxGroupWidth = 0;
        for (var i = 0; i < vm.groups.length; i++) {
          var group = vm.groups[i];
          var groupWidth = 0;
          for (var j = 0; j < group.effects.length; j++) {
            var effect = group.effects[j];
            var rectWidth = vm.getRectWidth(effect);
            groupWidth += horizontalSpaceBetweenEffects + rectWidth;
          }
          if (groupWidth > maxGroupWidth) {
            maxGroupWidth = groupWidth;
          }
        }

        vm.width = 2 * margin + maxGroupWidth;
      };

      vm.drawFrames = function() {
        vm.ctx.translate(margin, margin);
        for (var i = 0; i < vm.groups.length; i++) {
          vm.ctx.save();

          var group = vm.groups[i];
          for (var j = 0; j < group.effects.length; j++) {
            var effect = group.effects[j];
            var rectWidth = vm.getRectWidth(effect);
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
            vm.ctx.translate(rectWidth + horizontalSpaceBetweenEffects, 0);
          }

          vm.ctx.restore();
          vm.ctx.translate(0, rectHeight + verticalSpaceBetweenGroups);
        }
      };

      vm.drawKnobs = function(currentTime) {
        var currentFrameIndex = parseInt(currentTime * 44100 / vm.individual.neural_output.ksmps);
        vm.knobCanvas.width = vm.knobCanvas.width; // reset canvas
        vm.knobCtx.translate(10, 10);  // margin
        for (var i = 0; i < vm.groups.length; i++) {
          vm.knobCtx.save();

          var group = vm.groups[i];
          for (var j = 0; j < group.effects.length; j++) {
            var effect = group.effects[j];
            var rectWidth = parameterWidth * effect.parameters.length;
            vm.knobCtx.save();
            vm.knobCtx.translate(30, 40);

            for (var k = 0; k < effect.parameters.length; k++) {
              var parameter = effect.parameters[k];
              var parameterValue = vm.individual.neural_output.series_standardized[parameter.index][currentFrameIndex];

              vm.knobCtx.beginPath();
              vm.knobCtx.arc(0, 0, knobRadius + 2, knobStartAngle, knobStartAngle + parameterValue * knobEndAngleRelative);
              vm.knobCtx.stroke();

              vm.knobCtx.translate(parameterWidth, 0);
            }

            vm.knobCtx.restore();
            vm.knobCtx.translate(rectWidth + horizontalSpaceBetweenEffects, 0);
          }

          vm.knobCtx.restore();
          vm.knobCtx.translate(0, rectHeight + verticalSpaceBetweenGroups);
        }
      };

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
        for (i = 0; i < statsService.data.effect.parameter_names.length; i++) {
          var parameterName = statsService.data.effect.parameter_names[i];

          if (parameterName.indexOf('softmax_') === 0) {
            currentEffectIndex++;
          } else if (effectName !== 'new_layer') {
            vm.effects[currentEffectIndex].parameters.push({
              name: parameterName,
              index: i
            })
          }
        }

        vm.calculateDimensions();
        vm.canvas.width = vm.knobCanvas.width = vm.width;
        vm.canvas.height = vm.knobCanvas.height = vm.height;
        vm.$container.height(vm.height);
        vm.drawFrames();
      };

      vm.init();
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
