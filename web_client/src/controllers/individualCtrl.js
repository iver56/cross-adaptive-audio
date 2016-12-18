'use strict';

angular.module('crossAdaptiveAudioApp')
  .controller('IndividualCtrl', function($scope, statsService, communicationService, $http, debounce) {
    var vm = this;
    vm.individual = null;
    vm.individualDetails = null;
    vm.loading = true;
    vm.selectedSound = 'output_sound';
    vm.effectParameterMode = 'all_parameters';

    $scope.$watch(function() {
      return statsService.data &&
        statsService.data.generations &&
        statsService.data.generations[statsService.selectedGeneration - 1] &&
        statsService.data.generations[statsService.selectedGeneration - 1]
          .individuals[statsService.selectedIndividualIndex] &&
        statsService.data.generations[statsService.selectedGeneration - 1]
          .individuals[statsService.selectedIndividualIndex].id
    }, debounce(100, function() {
      if (statsService.data && statsService.data.generations && statsService.data.generations[statsService.selectedGeneration - 1]) {
        vm.individual = statsService.data.generations[statsService.selectedGeneration - 1]
          .individuals[statsService.selectedIndividualIndex];
        vm.fetchWholeIndividualRepresentation();
      }
    }));

    vm.fetchWholeIndividualRepresentation = function() {
      vm.loading = true;
      var url = '/individuals/' + statsService.selectedExperimentFolder +
        '/individual_' + vm.individual.id + '.json';
      $http.get(url).then(function(response) {
        vm.individualDetails = response.data;
        vm.calculateSoftmaxValues();
        vm.loading = false;
      }, function(response) {
        vm.loading = false;
        vm.individualDetails = null;
      });
    };

    vm.calculateSoftmaxValues = function() {
      if (statsService.data.args.effect_names.length === 1) {
        return; // N/A when only 1 effect
      }

      // Sorry about this unmaintainable mess
      var groups = [{effects: []}];
      var i, j, k, effectName, parameterName, softmaxIndex, effect, group;
      var currentGroupIndex = 0;
      var currentEffectIndex = 0;
      for (i = 0; i < statsService.data.args.effect_names.length - 1; i++) {
        effectName = statsService.data.args.effect_names[i];
        if (effectName === 'new_layer') {
          currentGroupIndex += 1;
          groups.push({effects: []});
        } else {
          groups[currentGroupIndex].effects.push({
            index: currentEffectIndex,
            name: effectName,
            softmaxValues: []}
            );
          currentEffectIndex++;
        }
      }

      var effectIndexToSoftmaxIndexMap = {};
      currentEffectIndex = 0;
      for (i = 0; i < vm.individualDetails.neural_output.order.length; i++) {
        parameterName = vm.individualDetails.neural_output.order[i];

        if (parameterName.indexOf('softmax_') === 0) {
          effectIndexToSoftmaxIndexMap[currentEffectIndex] = i;
          currentEffectIndex++;
        }
      }

      for (i = 0; i < groups.length; i++) {
        group = groups[i];

        for (j = 0; j < vm.individualDetails.neural_output.series_standardized[0].length; j++) {
          var softmaxDenominator = 0;
          for (k = 0; k < group.effects.length; k++) {
            effect = group.effects[k];
            softmaxIndex = effectIndexToSoftmaxIndexMap[effect.index];
            // hard coded extent -10 to 10, like in effect.py
            softmaxDenominator += Math.exp(-10 + 20 * vm.individualDetails.neural_output.series_standardized[softmaxIndex][j]);
          }
          for (k = 0; k < group.effects.length; k++) {
            effect = group.effects[k];
            softmaxIndex = effectIndexToSoftmaxIndexMap[effect.index];
            var softmaxValue = Math.exp(-10 + 20 * vm.individualDetails.neural_output.series_standardized[softmaxIndex][j]) / softmaxDenominator;
            effect.softmaxValues.push(softmaxValue);
          }
        }
      }

      var order = [];
      var seriesStandardized = [];
      for (i = 0; i < groups.length; i++) {
        group = groups[i];
        for (k = 0; k < group.effects.length; k++) {
          effect = group.effects[k];
          order.push(group.effects[k].name);
          seriesStandardized.push(effect.softmaxValues);
        }
        if (i != groups.length - 1) {
          order.push('new_layer');
          var emptySeries = [];
          for (var l = 0; l < vm.individualDetails.neural_output.series_standardized[0].length; l++) {
            emptySeries.push(0);
          }
          seriesStandardized.push(emptySeries);
        }
      }

      vm.individualDetails.softmax_values = {
        ksmps: vm.individualDetails.neural_output.ksmps,
        order: order,
        series_standardized: seriesStandardized
      };
    }
  });
