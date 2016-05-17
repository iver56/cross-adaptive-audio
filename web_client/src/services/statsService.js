(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('statsService', function($rootScope, $http) {
      var that = this;

      that.experimentFolders = null;
      that.selectedExperimentFolder = null;
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
          if (null === that.selectedGeneration || that.selectedGeneration > that.numGenerations) {
            that.selectedGeneration = that.numGenerations;
          }
          if (null === that.selectedIndividualIndex) {
            that.selectedIndividualIndex = that.getPopulationSize() - 1;
          }
        }
      };
      
      that.getPopulationSize = function() {
        return that.data.generations[that.selectedGeneration - 1].individuals.length;
      };

      $rootScope.$watch(function() {
        return that.selectedGeneration;
      }, function() {
        if (that.data && that.selectedIndividualIndex > that.getPopulationSize() - 1) {
          that.selectedIndividualIndex = that.getPopulationSize() - 1;
        }
      });

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
      
      that.setExperimentFolder = function(experimentFolder) {
        that.selectedExperimentFolder = experimentFolder;
        that.fetchStats(experimentFolder).then(function(response) {
          that.setData(response.data);
        }, function(response) {
          
        });
      };

      that.fetchStats = function(experimentFolder) {
        return $http.get('/stats/' + experimentFolder + '/stats.json');
      };

      $rootScope.$on('stats.json', function(event, message) {
        if (message.filePath.indexOf(that.selectedExperimentFolder) !== -1) {
          that.setData(message.data);
        }
      });

      $rootScope.$on('experimentFolders', function(event, data) {
        that.experimentFolders = data;
      })
    });
})();
