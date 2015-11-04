(function() {
    'use strict';

    var app = angular.module('PlayApp', ['play.services', 'play.controller', 'ngRoute', 'rzModule', 'ui.bootstrap']);
    app.value('apiUrl', '//localhost:8000/api');

    app.run(function($rootScope, $location, MeService) {
        $rootScope.me = MeService;
        MeService.init();
        $rootScope.searchForm = {term: ''};
        $rootScope.searchSubmit = function() {
            $location.path('/search/' + $rootScope.searchForm.term);
        };
    });


    app.config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
        $routeProvider.when('/playlists/:playlistId', {
            templateUrl: 'templates/tracklist/playlist.html',
            controller: 'PlaylistController',
            name: 'PlaylistView'
        }).when('/search/:term', {
            templateUrl: 'templates/tracklist/search.html',
            controller: 'SearchController',
            name: 'PlaylistView'
        });
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
    }]);


    app.filter('getByProperty', function () {
        return function (propertyName, propertyValue, collection) {
            var i = 0, len = collection.length;
            for (; i < len; i++) {
                if (collection[i][propertyName] == propertyValue) {
                    return collection[i];
                }
            }
            return null;
        };
    });


    app.filter('duration', function () {
        function divmod(x, y) {
            return [Math.floor(x / y), x % y];
        }

        return function (length) {
            if (!length)
                length = 0;
            length = Math.floor(length);
            var ms = divmod(length, 60);
            var m = ms[0];
            var s = ms[1];
            var hm = divmod(m, 60);
            var h = hm[0];
            m = hm[1];
            if (h > 0) {
                return ('0' + h).slice(h.toString().length > 2 ? 1 : 0) + ':' + ('0' + m).slice(-2) + ':' + ('0' + s).slice(-2);
            } else {
                return ('0' + m).slice(-2) + ':' + ('0' + s).slice(-2);
            }
        };
    });

    app.controller('SearchController', ['$scope', '$route', 'TrackService', 'ArtistService', function ($scope, $route, TrackService, ArtistService) {
        $scope.term = $route.current.params.term;
        $scope.search = {
            'tracks': TrackService.search($scope.term, {'embedded': {'owner': 1, 'tracks': 1}}),
            'artists': ArtistService.search($scope.term, {'embedded': {'owner': 1, 'tracks': 1}})};
    }]);


    app.controller('MePlaylistController', ['$scope', 'PlaylistRepository', 'MeService', function ($scope, PlaylistRepository, MeService) {
        $scope.newItem = {'name': '', 'show': false};
        $scope.me = MeService;
        $scope.updatePlaylist = function () {
            $scope.playlists = PlaylistRepository.query({'where': {'owner': MeService.user._id}});
        };
        $scope.showNewItem = function() {
            $scope.newItem.show=true;
            $scope.newItem.name = '';

        };
        $scope.submitNew = function () {
            PlaylistRepository.create({'name': $scope.newItem.name}, function () {
                $scope.newItem.show = false;
                $scope.updatePlaylist();
            });
        };

        $scope.playlist = [];
        MeService.user.$promise.then($scope.updatePlaylist);
    }]);

    app.controller('PlaylistController', ['$scope', '$route', 'PlaylistRepository', function ($scope, $route, PlaylistRepository) {
        $scope.playlist = PlaylistRepository.get($route.current.params.playlistId, {'embedded': {'owner': 1, 'tracks': 1}}) ;
    }]);

    app.directive('tracklist', ['Player', function (Player) {
        return {
            restrict: 'E',
            scope: {
                tracks: '=tracks    '
            },
            controller: function ($scope) {
                $scope.play = function(track) {
                    Player.play(track);
                };
            },
            templateUrl: 'templates/tracklist/tracks.html'

        };
    }]);

    app.directive('trackDropdown', ['Player', function (Player) {
        return {
            restrict: 'E',
            scope: {
                track: '=track'
            },
            controller: function($scope) {
                $scope.player = Player;
            },
            templateUrl: 'templates/track_dropdown.html'
        };
    }]);

    app.service('Player', ['apiUrl', function(apiUrl) {
        var service = this;
        this.queue = [];
        this.currentTrack = null;
        this.play = function(track) {
            service.clearQueue();
            service.queue.push(track);
            service.currentTrack = service.getNextTrack();
        };
        this.getNextTrack = function() {
            if (service.queue.length > 0) {
                service.currentTrack = service.queue.shift();
                return service.currentTrack;
            }
            return null;
        };
        this.addTrack = function (track) {
            service.queue.push(track);
        };
        this.clearQueue = function() {
            service.queue = [];
        };
        this.getStream = function(track) {
            return apiUrl + '/tracks/stream/' + track._id;
        };

    }]);

    app.directive('aplayer', function ($interval) {
        return {
            restrict: 'A',
            scope: {
                stream: '='
            },
            templateUrl: 'templates/audioplayer.html',
            link: function () {},
            controller: function ($scope, Player) {
                $scope.positionSlider = 0;
                $scope.volumeSlider = 50;
                $scope.volumeIcon = '';
                $scope.player = Player;
                $scope.audio = new Audio();

                $scope.audio.volume = 0.6;
                $scope.$watch('player.currentTrack', function () {
                    if ($scope.player.currentTrack) {
                        $scope.audio.src = $scope.player.getStream($scope.player.currentTrack);
                        $scope.play();
                    }
                });

                $scope.mute = function () {
                    $scope.audio.muted = !$scope.audio.muted;
                };

                $scope.play = function () {
                    if ($scope.audio.paused) {
                        $scope.audio.src == null;
                        $scope.player.getNextTrack();
                        $scope.audio.play();
                    } else {
                        $scope.audio.pause();
                    }
                };

                $scope.$watch('audio.paused', function (newval) {
                    if (newval) {
                        $scope.playButton = 'glyphicon-play';
                    } else {
                        $scope.playButton = 'glyphicon-pause';
                    }
                });

                $scope.$watch('audio.muted', function () {
                    $scope.volumeIcon = $scope.audio.muted ? 'glyphicon-volume-off' : 'glyphicon-volume-up';
                });

                $scope.$watch('audio.ended', function () {
                    $scope.player.getNextTrack();
                });

                $interval(function () {
                    $scope.ctime = $scope.audio.currentTime;
                    $scope.positionSlider = $scope.audio.currentTime;
                }, 100);

                $scope.changetime = function () {
                    $scope.audio.currentTime = $scope.positionSlider;
                };

                $scope.changevol = function () {
                    $scope.audio.volume = $scope.volumeSlider / 100;
                };
            }
        };
    });


}());
