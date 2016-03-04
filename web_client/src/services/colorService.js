(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .service('colorService', function() {
      var that = this;

      var maxDeviation = 3;

      that.negativeColor = [12, 108, 204]; // -maxDeviation
      that.neutralColor = [255, 255, 255]; // 0
      that.positiveColor = [204, 12, 60]; //[0, 109, 44]; // maxDeviation

      that.getColor = function(standardizedValue) {
        var amountToMix = Math.min(Math.abs(standardizedValue), maxDeviation) / maxDeviation;
        if (standardizedValue < 0) {
          return that.colorMixer(that.neutralColor, that.negativeColor, amountToMix);
        } else {
          return that.colorMixer(that.neutralColor, that.positiveColor, amountToMix);
        }
      };

      // http://stackoverflow.com/a/32171077/2319697
      //colorChannelA and colorChannelB are ints ranging from 0 to 255
      that.colorChannelMixer = function(colorChannelA, colorChannelB, amountToMix) {
        var channelA = colorChannelA * (1 - amountToMix);
        var channelB = colorChannelB * amountToMix;
        return parseInt(channelA + channelB);
      };

      //rgb1 and rgb2 are arrays, amountToMix ranges from 0.0 to 1.0
      //example (red): rgb1 = [255,0,0]
      that.colorMixer = function(rgb1, rgb2, amountToMix) {
        var r = that.colorChannelMixer(rgb1[0], rgb2[0], amountToMix);
        var g = that.colorChannelMixer(rgb1[1], rgb2[1], amountToMix);
        var b = that.colorChannelMixer(rgb1[2], rgb2[2], amountToMix);
        return "rgb(" + r + "," + g + "," + b + ")";
      };

    });
})();
