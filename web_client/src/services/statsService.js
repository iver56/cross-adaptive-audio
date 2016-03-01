(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('statsService', function() {
      var that = this;

      that.data = [];
      that.selectedGeneration = 1;
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
          that.numGenerations = data.length;
          that.data = data;
          that.populationSize = data[0].fitness_values.length;
        }
      };

      that.getHistogramData = function() {
        var bins = [];
        var fitnessValues = that.data[that.selectedGeneration - 1].fitness_values;
        for (var i = 0; i < that.histogramOptions.numBins; i++) {
          var bin = {
            minValue: that.histogramOptions.minValue + i * that.histogramOptions.step,
            maxValue: that.histogramOptions.minValue + (i + 1) * that.histogramOptions.step,
            numOccurrences: 0
          };
          bins.push(bin);
        }
        for (var i = fitnessValues.length; i--;) {
          var binIndex = Math.max(
            Math.min(
              parseInt(that.histogramOptions.numBins * (fitnessValues[i] - that.histogramOptions.minValue) / that.histogramOptions.difference),
              that.histogramOptions.numBins - 1
            ),
            0
          );
          bins[binIndex].numOccurrences += 1;
        }
        return bins;
      }
    });
})();
