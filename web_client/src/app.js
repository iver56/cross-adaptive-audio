angular
  .module('crossAdaptiveAudioApp', [
    'n3-line-chart',
    'ngMaterial',
    'rt.debounce'
  ])
  .run(function(communicationService) {
    communicationService.init();
  })
  .constant('sampleRate', 44100)
;
