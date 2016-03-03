(function() {
  'use strict';

  angular
    .module('crossAdaptiveAudioApp')
    .directive('waveform', Waveform);

  function Waveform() {

    function WaveformCtrl($scope, debounce) {
      var vm = this;

      vm.wavesurfer = window.WaveSurfer.create({
        container: '#waveform-container',
        waveColor: 'violet',
        progressColor: 'purple'
      });

      function sanitizeFilePath(filePath){
        return filePath.replace(/^\.\//, '/').replace(/\\/g, '/');
      }

      vm.wavesurfer.on('ready', function () {
        console.log('wavesurfer is ready for action');
        vm.isReady = true;
        if (!$scope.$$phase) {
          $scope.$apply();
        }
      });

      vm.wavesurfer.on('finish', function () {
        console.log('wavesurfer is finished playing');
        if (!$scope.$$phase) {
          $scope.$apply();
        }
      });

      $scope.$watch(function() {
        return vm.sound;
      }, debounce(100, function() {
        vm.isReady = false;
        vm.wavesurfer.load(sanitizeFilePath(vm.sound));
      }));

      vm.onKeyUp = function (e) {
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
        }
      };

      vm.init = function () {
        window.addEventListener("keyup", vm.onKeyUp, false);
      };
      vm.init();

      $scope.$on("$destroy", function () {
        window.removeEventListener("keyup", vm.onKeyUp, false);
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
