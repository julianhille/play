(function() {
    'use strict';

    var app = angular.module('PlayApp', ['play.services', 'play.controller', 'ngRoute', 'rzModule', 'ui.bootstrap']);

    app.run(function runApp($rootScope, $location, MeService) {
        $rootScope.me = MeService;
        MeService.init();
        $rootScope.searchForm = {term: ''};
        $rootScope.searchSubmit = function searchSubmit() {
            $location.url('/search?q=' + $rootScope.searchForm.term);
        };
    });


    app.config(['$routeProvider', '$httpProvider', function appConfig($routeProvider, $httpProvider) {
        $routeProvider.when('/playlists/:playlistId', {
            templateUrl: 'templates/tracklist/playlist.html',
            controller: 'PlaylistController',
            name: 'PlaylistView'
        }).when('/my/:playlistId', {
            templateUrl: 'templates/tracklist/myplaylist.html',
            controller: 'MyPlaylistController',
            name: 'MyPlaylistView'
        }).when('/search', {
            templateUrl: 'templates/tracklist/search.html',
            controller: 'SearchController',
            name: 'PlaylistView'
        });
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
        $httpProvider.interceptors.push([
            '$injector',
            function AuthInterceptor($injector) {
                return $injector.get('AuthInterceptor');
            }
        ],[
            '$injector',
            function EtagInterceptor($injector) {
                return $injector.get('EtagInterceptor');
            }
        ]);
    }]);


    app.filter('getByProperty', function getByPropertyFilter() {
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


    app.filter('duration', function durationFilter() {
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

    app.controller('SearchController', ['$scope', '$route', 'TrackService', 'ArtistService', function SearchController($scope, $route, TrackService, ArtistService) {
        $scope.term = $route.current.params.q;
        if ($scope.term.length > 0) {
            $scope.search = {
                'tracks': TrackService.search($scope.term, {'embedded': {'owner': 1, 'tracks': 1}}),
                'artists': ArtistService.search($scope.term, {'embedded': {'owner': 1, 'tracks': 1}})};
        }
    }]);


    app.controller('MePlaylistController', ['$scope', 'MePlaylistService', function MePlaylistController($scope, MePlaylistService) {
        $scope.newItem = {'name': '', 'show': false};

        $scope.showNewItem = function showNewItem() {
            $scope.newItem.show=true;
            $scope.newItem.name = '';

        };

        $scope.submitNew = function submitNew() {
            MePlaylistService.create($scope.newItem.name, function successCallback(){
                $scope.newItem.show = false;
            });
        };
        $scope.playlists = MePlaylistService.playlists;
    }]);

    app.controller('MyPlaylistController', ['$scope', '$filter', '$route', 'PlaylistRepository', 'MePlaylistService', function MyPlaylistController($scope, $filter, $route, PlaylistRepository, MePlaylistService) {
        var playlistId = $route.current.params.playlistId;
        MePlaylistService.playlists.$promise.then(function successCallback(){
            $scope.playlist = $filter('getByProperty')('_id', playlistId, MePlaylistService.playlists._items);
        });
    }]);

    app.controller('PlaylistController', ['$scope', '$filter', '$route', 'PlaylistRepository', function PlaylistController($scope, $filter, $route, PlaylistRepository) {
        var playlistId = $route.current.params.playlistId;
        $scope.playlist = PlaylistRepository.get(playlistId, {'embedded': {'owner': 1, 'tracks': 1}}) ;
    }]);

    app.directive('tracklist', ['Player', function tracklistDirective(Player) {
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

    app.directive('trackDropdown', ['Player', function trackDropdownDirective(Player) {
        return {
            restrict: 'E',
            scope: {
                track: '=track',
                playlist: '=playlist',
                trackIndex: '=trackIndex'
            },
            controller: function controller($scope, MePlaylistService) {
                $scope.player = Player;
                $scope.query = '';
                $scope.playlists = MePlaylistService.playlists._items;
                $scope.trackToPlaylist = function trackToPlaylist(track, playlist) {
                    MePlaylistService.addTrack(track, playlist);
                };
                $scope.removeTrackFromPlaylist = function removeTrackFromPlaylist(index, playlist) {
                    MePlaylistService.removeTrack(index, playlist);
                };
            },
            templateUrl: 'templates/track_dropdown.html'
        };
    }]);

    app.service('Player', ['apiUrl', '$rootScope', function PlayerService(apiUrl, $rootScope) {
        var service = this;
        this.queue = [];

        var playNextTrack = function playNextTrack() {
            if (service.queue.length > 0) {
                var track = service.queue.shift();
                service.play(track);
            }
            return null;
        };
        var getStream = function getStream(track) {
            return apiUrl + '/tracks/stream/' + track._id;
        };
        this.play = function play(track) {
            $rootScope.$broadcast('audio.play', track, getStream(track));
        };
        this.addTrack = function addTrack(track) {
            service.queue.push(track);
        };
        this.clearQueue = function clearQueue() {
            service.queue = [];
        };

        $rootScope.$on('audio.nextTrack', function rootOnNextTrack(){
            playNextTrack();
        });
    }]);

    app.directive('aplayer', function aplayerDirective($interval) {
        return {
            restrict: 'A',
            scope: {
                stream: '='
            },
            templateUrl: 'templates/audioplayer.html',
            link: function link() {},
            controller: function controller($scope, $rootScope, Player) {
                $rootScope.$on('audio.play', function onAudioPlay(event, track, stream){
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

                $scope.mute = function mute() {
                    $scope.audio.muted = !$scope.audio.muted;
                };

                $scope.play = function play() {
                    if ($scope.audio.paused) {
                        if($scope.audio.src !== null) {
                            $scope.audio.play();
                        }
                    } else {
                        $scope.audio.pause();
                    }
                };

                $scope.playNext = function playNext() {
                    $rootScope.$broadcast('audio.nextTrack');
                };

                $scope.audio.addEventListener('play', function playEventListener(){
                    if (!$scope.audio.error && !!$scope.audio.src) {
                        $scope.playButton = 'glyphicon-pause';
                    } else {
                        $scope.audio.pause();
                        $scope.playNext();
                    }
                });
                $scope.audio.addEventListener('ended', function endedEventListener(){ $scope.playNext();});
                $scope.audio.addEventListener('pause', function pauseEventListener(){ $scope.playButton = 'glyphicon-play';});
                $scope.audio.addEventListener('muted', function mutedEventListener(){ $scope.volumeIcon = $scope.audio.muted ? 'glyphicon-volume-off' : 'glyphicon-volume-up';});
                $scope.audio.addEventListener('error', function errorEventListener(){
                    $scope.audio.pause();
                    $scope.playNext();
                });


                $interval(function audioDirectiveInterval() {
                    $scope.positionSlider = $scope.audio.currentTime;
                }, 100);

                $scope.changetime = function changetime() {
                    $scope.audio.currentTime = $scope.positionSlider;
                };

                $scope.changevol = function changevol() {
                    $scope.audio.volume = $scope.volumeSlider / 100;
                };
            }
        };
    });


    app.service('MePlaylistService', ['PlaylistRepository', 'MeService', '$rootScope', 'AUTH_EVENTS', function MePlaylistService(PlaylistRepository, MeService, $rootScope, AUTH_EVENTS){
        var service = this;

        var createTrackList = function createTrackList(playlist) {
            var tracks = [];
            playlist.tracks.forEach(function(item){
                if (typeof item == 'string')
                    tracks.push(item);
                else
                    tracks.push(item._id);
            });
            return tracks;
        };

        $rootScope.$on(AUTH_EVENTS.loginSuccess, function onLoginSuccess() {
            service.update();
        });

        $rootScope.$on(AUTH_EVENTS.logoutSuccess, function onLogoutSuccess() {
            service.playlists = null;
        });
        this.update = function update() {
            service.playlists = PlaylistRepository.query({'where': {'owner': MeService.user._id}});
        };


        this.create = function create(name, success, error) {
            PlaylistRepository.create({'name': name}, function successCallback(data) {
                if (success)
                    success(data);
                service.update();
            }, function errorCallback(response) {
                if (error)
                    error(response);
            });
        };

        this.removeTrack = function removeTrack(index, playlist) {
            var tracks = createTrackList(playlist);
            tracks.splice(index, 1);
            PlaylistRepository.patch(playlist, {'tracks': tracks}, function successCallback() {
                playlist.tracks.splice(index, 1);
            });
        };

        this.addTrack = function addTrack(track, playlist) {
            var tracks = createTrackList(playlist);
            tracks.push(track._id);
            PlaylistRepository.patch(playlist, {'tracks': tracks}, function successCallback() {
                playlist.tracks.push(track);
            });
        };

        this.playlists = null;
        if (MeService.isLoggedIn()) {
            service.update();
        }

    }]);
}());
