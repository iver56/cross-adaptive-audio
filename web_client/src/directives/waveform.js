(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('waveform', Waveform);

  function Waveform() {

    function WaveformCtrl($scope, debounce, sampleRate, $rootScope, $element, statsService) {
      var vm = this;

      vm.container = $($element[0]).find('.waveform-container')[0];

      vm.updatePlaybackRate = function() {
        vm.mappedPlaybackRate = Math.pow(vm.playbackRate, 3);
        vm.wavesurfer.setPlaybackRate(vm.mappedPlaybackRate);
      };

      vm.resetPlaybackRate = function() {
        vm.playbackRate = 1.0;
        vm.updatePlaybackRate();
      };

      vm.wavesurfer = window.WaveSurfer.create({
        container: vm.container,
        waveColor: 'violet',
        progressColor: 'purple',
        fillParent: false,
        minPxPerSec: sampleRate / vm.sound.feature_data.ksmps,
        scrollParent: true
      });

      vm.getFilePath = function() {
        return '/' + (
            vm.sound.is_input ? 'input' : 'output/' + statsService.selectedExperimentFolder
          ) + '/' + vm.sound.filename;
      };

      vm.wavesurfer.on('ready', function() {
        vm.isReady = true;
        if (!$scope.$$phase) {
          $scope.$apply();
        }
      });

      vm.wavesurfer.on('finish', function() {
        if (!$scope.$$phase) {
          $scope.$apply();
        }
      });

      vm.wavesurfer.on('scroll', function(e) {
        $rootScope.$emit('waveform.scroll', {
          scrollLeft: e.target.scrollLeft
        });
      });

      vm.wavesurfer.on('audioprocess', function(e) {
        $rootScope.$emit('waveform.audioprocess', e);
      });

      $scope.$watch(function() {
        return vm.sound && vm.sound.filename;
      }, debounce(100, function() {
        vm.isReady = false;
        vm.wavesurfer.load(vm.getFilePath());
      }));

      vm.onKeyUp = function(e) {
        var noOp = false;
        if (e.keyCode === 32) {  // space
          if (vm.isReady) {
            vm.wavesurfer.playPause();
          }
        } else {
          // no operation
          noOp = true;
        }
        if (!noOp) {
          if (!$scope.$$phase) {
            $scope.$apply();
          }
          e.preventDefault();
        }
      };

      vm.init = function() {
        window.addEventListener("keydown", vm.onKeyUp, false);
        vm.resetPlaybackRate();
      };
      vm.init();

      $scope.$on("$destroy", function() {
        window.removeEventListener("keydown", vm.onKeyUp, false);
        vm.wavesurfer.destroy();
      });
    }

    return {
      restrict: 'E',
      scope: {},
      bindToController: {
        sound: '='
      },
      templateUrl: 'views/waveform.html',
      controller: WaveformCtrl,
      controllerAs: 'wf'
    };
  }
})();
