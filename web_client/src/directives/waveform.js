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
        console.log('loading')
      }));
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
