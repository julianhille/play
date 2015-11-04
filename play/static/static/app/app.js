(function() {
    'use strict';

    var app = angular.module('PlayApp', ['play.services', 'play.controller', 'ngRoute', 'rzModule', 'ui.bootstrap']);

    app.run(function($rootScope, $location, MeService, MePlaylistService) {
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
        }).when('/my/:playlistId', {
            templateUrl: 'templates/tracklist/myplaylist.html',
            controller: 'MyPlaylistController',
            name: 'MyPlaylistView'
        }).when('/search/:term', {
            templateUrl: 'templates/tracklist/search.html',
            controller: 'SearchController',
            name: 'PlaylistView'
        });
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
        $httpProvider.interceptors.push([
            '$injector',
            function ($injector) {
                return $injector.get('AuthInterceptor');
            }
        ],[
            '$injector',
            function ($injector) {
                return $injector.get('EtagInterceptor');
            }
        ]);
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


    app.controller('MePlaylistController', ['$scope', 'MePlaylistService', function ($scope, MePlaylistService) {
        $scope.newItem = {'name': '', 'show': false};

        $scope.showNewItem = function() {
            $scope.newItem.show=true;
            $scope.newItem.name = '';

        };

        $scope.submitNew = function () {
            MePlaylistService.create($scope.newItem.name, function(data){
                $scope.newItem.show = false;
            });
        };
        $scope.playlists = MePlaylistService.playlists;
    }]);

    app.controller('MyPlaylistController', ['$scope', '$filter', '$route', 'PlaylistRepository', 'MePlaylistService', function ($scope, $filter, $route, PlaylistRepository, MePlaylistService) {
        var playlistId = $route.current.params.playlistId;
        MePlaylistService.playlists.$promise.then(function(){
            $scope.playlist = $filter('getByProperty')('_id', playlistId, MePlaylistService.playlists._items);
        });
    }]);

    app.controller('PlaylistController', ['$scope', '$filter', '$route', 'PlaylistRepository', 'MePlaylistService', function ($scope, $filter, $route, PlaylistRepository, MePlaylistService) {
        var playlistId = $route.current.params.playlistId;
        $scope.playlist = PlaylistRepository.get(playlistId, {'embedded': {'owner': 1, 'tracks': 1}}) ;
    }]);

    app.directive('tracklist', ['Player', function (Player) {
        return {
            restrict: 'E',
            scope: {
                tracks: '=tracks',
                playlist: '=playlist'
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
                track: '=track',
                playlist: '=playlist',
                trackIndex: '=trackIndex'
            },
            controller: function($scope, MePlaylistService) {
                $scope.player = Player;
                $scope.query = '';
                $scope.playlists = MePlaylistService.playlists._items;
                $scope.trackToPlaylist = function(track, playlist) {
                    MePlaylistService.addTrack(track, playlist);
                };
                $scope.removeTrackFromPlaylist = function(index, playlist) {
                    MePlaylistService.removeTrack(index, playlist);
                };
            },
            templateUrl: 'templates/track_dropdown.html'
        };
    }]);

    app.service('Player', ['apiUrl', '$rootScope', function(apiUrl, $rootScope) {
        var service = this;
        this.queue = [];

        var playNextTrack = function() {
            if (service.queue.length > 0) {
                var track = service.queue.shift();
                service.play(track);
            }
            return null;
        };
        var getStream = function(track) {
            return apiUrl + '/tracks/stream/' + track._id;
        };
        this.play = function(track) {
            $rootScope.$broadcast('audio.play', track, getStream(track));
        };
        this.addTrack = function (track) {
            service.queue.push(track);
        };
        this.clearQueue = function() {
            service.queue = [];
        };

        $rootScope.$on('audio.nextTrack', function(){
            playNextTrack();
        });
    }]);

    app.directive('aplayer', function ($interval) {
        return {
            restrict: 'A',
            scope: {
                stream: '='
            },
            templateUrl: 'templates/audioplayer.html',
            link: function () {},
            controller: function ($scope, $rootScope, Player) {
                $rootScope.$on('audio.play', function(event, track, stream){
                    $scope.audio.src = stream;
                    $scope.currentTrack = track;
                    $scope.play();

                });

                $scope.playButton = 'glyphicon-play';
                $scope.positionSlider = 0;
                $scope.volumeSlider = 50;
                $scope.volumeIcon = '';
                $scope.player = Player;
                $scope.queue = Player.queue;
                $scope.audio = new Audio();

                $scope.audio.volume = 0.6;

                $scope.mute = function () {
                    $scope.audio.muted = !$scope.audio.muted;
                };

                $scope.play = function () {
                    if ($scope.audio.paused) {
                        if($scope.audio.src !== null) {
                            $scope.audio.play();
                        }
                    } else {
                        $scope.audio.pause();
                    }
                };

                $scope.playNext = function() {
                    $rootScope.$broadcast('audio.nextTrack');
                };

                $scope.audio.addEventListener('play', function(){
                    if (!$scope.audio.error && !!$scope.audio.src) {
                        $scope.playButton = 'glyphicon-pause';
                    } else {
                        $scope.audio.pause();
                        $scope.playNext();
                    }
                });
                $scope.audio.addEventListener('ended', function(){ $scope.playNext();});
                $scope.audio.addEventListener('pause', function(){ $scope.playButton = 'glyphicon-play';});
                $scope.audio.addEventListener('muted', function(){ $scope.volumeIcon = $scope.audio.muted ? 'glyphicon-volume-off' : 'glyphicon-volume-up';});
                $scope.audio.addEventListener('error', function(){
                    $scope.audio.pause();
                    $scope.playNext();
                });


                $interval(function () {
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


    app.service('MePlaylistService', ['PlaylistRepository', 'MeService', '$rootScope', 'AUTH_EVENTS', function(PlaylistRepository, MeService, $rootScope, AUTH_EVENTS){
        var service = this;

        var createTrackList = function(playlist) {
            var tracks = [];
            playlist.tracks.forEach(function(item){
                if (typeof item == 'string')
                    tracks.push(item);
                else
                    tracks.push(item._id);
            });
            return tracks;
        };

        $rootScope.$on(AUTH_EVENTS.loginSuccess, function() {

            service.update();
        });

        $rootScope.$on(AUTH_EVENTS.logoutSuccess, function() {
            service.playlists = null;
        });
        this.update = function() {
            service.playlists = PlaylistRepository.query({'where': {'owner': MeService.user._id}});
        };


        this.create = function(name, success, error) {
            PlaylistRepository.create({'name': name}, function (data) {
                if (success)
                    success(data);
                service.update();
            }, function (response) {
                if (error)
                    error(response);
            });
        };

        this.removeTrack = function(index, playlist) {
            var tracks = createTrackList(playlist);
            tracks.splice(index, 1);
            PlaylistRepository.patch(playlist, {'tracks': tracks}, function() {
                playlist.tracks.splice(index, 1);
            });
        };

        this.addTrack = function(track, playlist) {
            var tracks = createTrackList(playlist);
            tracks.push(track._id);
            PlaylistRepository.patch(playlist, {'tracks': tracks}, function() {
                playlist.tracks.push(track);
            });
        };

        this.playlists = null;

    }]);
}());
