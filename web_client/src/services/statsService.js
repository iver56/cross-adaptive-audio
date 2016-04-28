(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('statsService', function($rootScope) {
      var that = this;

      that.data = null;
      that.selectedGeneration = null;
      that.selectedIndividualIndex = null;
      that.numGenerations = 1;
      that.populationSize = null;
      that.histogramOptions = {
        numBins: 200,
        minValue: 0.0,
        maxValue: 1.0
      };
      that.histogramOptions.difference = that.histogramOptions.maxValue - that.histogramOptions.minValue;
      that.histogramOptions.step = that.histogramOptions.difference / that.histogramOptions.numBins;

      that.setData = function(data) {
        if (data) {
          that.numGenerations = data.generations.length;
          that.data = data;
          that.populationSize = data.generations[that.numGenerations - 1].individuals.length;
          if (null === that.selectedGeneration) {
            that.selectedGeneration = that.numGenerations;
          }
          if (null === that.selectedIndividualIndex || that.selectedIndividualIndex > that.populationSize - 1) {
            that.selectedIndividualIndex = that.populationSize - 1;
          }
        }
      };

      that.getHistogramData = function() {
        var bins = [];
        var individuals = that.data.generations[that.selectedGeneration - 1].individuals;
        for (var i = 0; i < that.histogramOptions.numBins; i++) {
          var bin = {
            minValue: that.histogramOptions.minValue + i * that.histogramOptions.step,
            maxValue: that.histogramOptions.minValue + (i + 1) * that.histogramOptions.step,
            numOccurrences: 0
          };
          bins.push(bin);
        }
        for (var i = individuals.length; i--;) {
          var binIndex = Math.max(
            Math.min(
              parseInt(
                that.histogramOptions.numBins
                * (individuals[i].fitness - that.histogramOptions.minValue)
                / that.histogramOptions.difference
              ),
              that.histogramOptions.numBins - 1
            ),
            0
          );
          bins[binIndex].numOccurrences += 1;
        }
        return bins;
      };

      $rootScope.$on('stats.json', function(event, data) {
        that.setData(data);
      })
    });
})();
