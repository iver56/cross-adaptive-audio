angular
  .module('crossAdaptiveAudioApp', [
    'n3-line-chart'
  ])
  .run(function(communicationService) {
    communicationService.init();
  })
;
