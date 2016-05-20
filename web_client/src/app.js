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
  .filter('capitalize', function() {
    return function(input) {
      return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
  })
;
