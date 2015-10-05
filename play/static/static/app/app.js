'use strict';


var k = 0;






var app = angular.module('PlayApp', ['ngRoute', 'rzModule'])
app.value('apiUrl', '//localhost:8000/api')

app.config(['$httpProvider', function ($httpProvider) {
    delete $httpProvider.defaults.headers.common['X-Requested-With'];

}]);

app.filter('getByProperty', function() {
    return function(propertyName, propertyValue, collection) {
        var i=0, len=collection.length;
        for (; i<len; i++) {
            if (collection[i][propertyName] == propertyValue) {
                return collection[i];
            }
        }
        return null;
    }
});


app.filter('duration', function() {
    function divmod(x, y) {
        return [Math.floor(x/y),  x % y]
    }

    return function(length) {
        if (!length)
            length = 0;
        length = Math.floor(length)
        var ms = divmod(length, 60);var m = ms[0];var s = ms[1];
        var hm = divmod(m, 60); var h = hm[0]; var m = hm[1];
        if (h > 0) {
            return ('0'+h).slice(h.toString().length > 2 ? 1 : 0) + ':' + ('0'+m).slice(-2) + ':' + ('0'+s).slice(-2);
        } else {
            return ('0'+m).slice(-2) + ':' + ('0'+s).slice(-2);
        }
    }
});


app.controller('LoginController', ['$scope', '$element', 'UserService', function($scope, $element, UserService) {

}]);



app.controller('PlaylistController', ['$scope', 'PlaylistRepository', 'TrackListService', function($scope, PlaylistRepository, TrackListService) {
    $scope.go = function(playlist_id) {
         PlaylistRepository.getPlaylist(
            function (data) {TrackListService.setPlaylist(data)},
            playlist_id)
    }
    $scope.playlist = null
    PlaylistRepository.getPlaylists(function(data) {$scope.playlists = data;});
}]);

app.controller('TracksController', ['$scope', '$filter', 'TrackListService', 'TrackService', function($scope, $filter, TrackListService, TrackService) {
    $scope.trackListService = TrackListService;
    $scope.trackService = TrackService
    $scope.play = function(track_id) {
        var track = $filter('getByProperty')('_id', track_id, $scope.trackListService.trackList.tracks);
        $scope.trackService.setTrack(track)
    };
}]);

app.service('TrackListService', function() {
    var trackList = {};
    var trackListType = '';
    this.setPlaylist =  function(playlist) {
            this.trackList = playlist;
            this.trackListType = 'playlist';
    }
    this.trackList = trackList
});


app.service('TrackService', function() {
    this.track = null;
    this.setTrack =  function(track) {
            this.track = track;
    }
});


app.service('UserService', ['apiUrl', '$http' , function(apiUrl, $http) {
    var user = null;
    return {
        login : function (username, password, remember) {
            return $http.post(
                apiUrl + '/users/login',
                {username: username, password: password, remember: remember});
        },
        logout : function () {
            return $http.post(
                apiUrl + '/users/logout',
                {username: username, password: password, remember: remember});
        },
        me: function () {
            return user;
        }
    }
}]);



var apiModule = angular.module('Play.Repositories', ['apiUrl']);

app.service('CsrfRepository', ['apiUrl', '$http' , function(apiUrl, $http) {
    return {
        getCsrfToken : function (callback) {
            $http.get(apiUrl + '/csrf').success(function(data){
               callback (data);
            });
        }
    }

}]);


app.service('PlaylistRepository', function(apiUrl, $http) {
    this.getPlaylists = function (callback) {
        $http.get(apiUrl + '/playlists?embedded={"tracks": 1, "owner": 1}').success(function(data){
            callback(data);
        });
    };
    this.getPlaylist = function (callback, id) {
        $http.get(apiUrl + '/playlists/'+ id +'/?embedded={"tracks": 1, "owner": 1}').success(function(data){
            callback (data);
        });
    };
});


app.service('TracksRepository', function(apiUrl, $http) {
    this.getTrack = function (callback, id) {
        $http.get(apiUrl + '/track/' + id).success(function(data){
               callback (data);
        });
    }
    this.getStream = function(callback, id) {
        return callback(apiUrl + '/stream/' + id);
    }
});


app.directive('aplayer',function($interval) {
    return {
        restrict:'A',
        scope: {
            stream: '='

        },
        templateUrl: '/audioplayer.html',
        link: function($scope, element, attrs){
        },
        controller: function($scope, TrackService, TracksRepository){
            console.log(TrackService.track)
            $scope.positionSlider = 0
            $scope.volumeSlider = 50
            $scope.volumeIcon =
            $scope.trackService = TrackService;

            $scope.audio = new Audio();

            $scope.audio.volume = 0.6;
            $scope.$watch('trackService.track', function(newval){
                if ($scope.trackService.track)
                     TracksRepository.getStream(function(link) {$scope.audio.src = link}, $scope.trackService.track._id);
            });

            $scope.mute = function() {
                $scope.audio.muted = !$scope.audio.muted;
            };
            $scope.play = function(){
                if($scope.audio.paused) {
                    $scope.audio.play();
                } else {
                    $scope.audio.pause();
                }
            };
            $scope.$watch('audio.paused', function(newval) {
                if (newval) {
                    $scope.playButton = 'glyphicon-play';
                } else {
                    $scope.playButton = 'glyphicon-pause';
                }
            });
            $scope.$watch('audio.muted', function(newval) {
                $scope.volumeIcon = $scope.audio.muted ?  'glyphicon-volume-off' : 'glyphicon-volume-up';
            });
            $interval(function(){
                $scope.ctime = $scope.audio.currentTime;
                $scope.positionSlider = $scope.audio.currentTime;
            }, 100);
            $scope.changetime = function(){
                $scope.audio.currentTime = $scope.positionSlider;
            };
            $scope.changevol = function(t){
                $scope.audio.volume = $scope.volumeSlider / 100;
            };
        }
    };
});
