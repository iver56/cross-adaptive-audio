angular
  .module('crossAdaptiveAudioApp', [
    'n3-line-chart',
    'ngMaterial'
  ])
  .run(function(communicationService) {
    communicationService.init();
  })
;
