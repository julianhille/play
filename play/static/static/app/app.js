'use strict';



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

app.controller('MainController', ['$scope', 'UserService', function($scope, UserService){
    $scope.userService = UserService
    UserService.me();
}]);


app.controller('SearchController', ['$scope', '$filter', 'TracksRepository', 'TrackService', 'TrackListService', function($scope, $filter, TracksRepository, TrackService, TrackListService){
    $scope.searchtext = 'some_file';
    $scope.tracks = [];
    $scope.trackService = TrackService;
    $scope.trackListService = TrackListService;
    $scope.play = function(track_id) {
        var track = $filter('getByProperty')('_id', track_id, $scope.tracks._items);
        $scope.trackService.setTrack(track)
    };
    $scope.searchAsYouType = function() {
        return;
        if ($scope.searchtext) {
            TracksRepository.search(function(data){
                $scope.tracks=data;
            }, $scope.searchtext, 3);
        }
    }
    $scope.searchSubmit = function() {
        if ($scope.searchtext) {

            // @Todo(jhille): we need to update the playlist controller
            TracksRepository.search(function(data){$scope.trackListService.setSearch(data);}, $scope.searchtext);
        }
    }
}]);

app.controller('LoginController', ['$scope', 'UserService', function($scope, UserService) {
    $scope.name = "";
    $scope.password = "";
    $scope.remember = false;
    $scope.submit = function() {
        UserService.login(function(data) {}, $scope.name, $scope.password, $scope.remember);
        return false;
    }
}]);



app.controller('PlaylistController', ['$scope', 'PlaylistRepository', 'TrackListService', 'UserService', function($scope, PlaylistRepository, TrackListService, UserService) {
    $scope.new_item = 0
    $scope.updatePlaylist = function() {
        PlaylistRepository.getUserPlaylists(function(data) {$scope.playlists = data;}, UserService.user._id);
    }

    $scope.submitNew =  function($event) {
        if($event.keyCode == 13) {
            PlaylistRepository.createPlaylist(function() {
                $scope.new_item = 0;
                $event.srcElement.value = ''
                $scope.updatePlaylist();
            }, $event.srcElement.value);

        }
        
    }
    $scope.go = function(playlist_id) {
         PlaylistRepository.getPlaylist(
            function (data) {TrackListService.setPlaylist(data)},
            playlist_id)
    }
    $scope.playlist = [];
    $scope.updatePlaylist();
}]);

app.controller('TracksController', ['$scope', '$filter', 'TrackListService', 'TrackService', function($scope, $filter, TrackListService, TrackService) {
    $scope.trackListService = TrackListService;
    $scope.trackService = TrackService
    $scope.play = function(tracks, track_id) {
        var track = $filter('getByProperty')('_id', track_id, tracks);
        $scope.trackService.setTrack(track)
    };
}]);

app.service('TrackListService', function() {
    var trackList = {};
    var trackListType = '';
    this.setPlaylist =  function(playlist) {
            this.trackList = playlist;
            this.type = 'playlist';
    }
    this.setSearch =  function(search) {
            this.trackList = search;
            this.type = 'search';
    }
    this.trackList = trackList;
    this.type = trackListType;
});


app.service('TrackService', function() {
    this.track = null;
    this.setTrack =  function(track) {
            this.track = track;
    }
});


app.service('UserService', ['apiUrl', '$http' , function(apiUrl, $http) {
    this.user = null;
    var service = this;
    this.login = function (callback, username, password, remember) {
        $http.post(
            apiUrl + '/me/login',
            {username: username, password: password, remember: remember}).success(function(data){
                service.user = data;
                if (typeof callback != 'undefined'){
                    callback(data);
                }
            });
    };
    this.logout = function (callback) {
        $http.post(
            apiUrl + '/me/logout').success(function(data){
                service.user = null;
                if (typeof callback != 'undefined'){
                    callback(data);
                }
            });
    };
    this.me = function (callback) {
        $http.get(apiUrl + '/me/').success(function(data) {
            service.user = data;
            if (typeof callback != 'undefined'){
                callback(data);
            }

        });
    };
    
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
    this.getPlaylists = function (callback, where) {
        where =  where ? '&where=' + JSON.stringify(where) : '';
        $http.get(apiUrl + '/playlists?embedded={"tracks": 1, "owner": 1}' + where).success(function(data){
            callback(data);
        });
    };
    this.getUserPlaylists = function (callback, user_id) {
        this.getPlaylists(callback, {'owner': user_id})
    };
    this.getPlaylist = function (callback, id) {
        $http.get(apiUrl + '/playlists/'+ id +'/?embedded={"tracks": 1, "owner": 1}').success(function(data){
            callback (data);
        });
    };
    this.createPlaylist = function(callback, playlist_name){
        $http.post(apiUrl + '/playlists/', {'name': playlist_name}).success(function(data){
            callback(data);
        });

    };
});


app.service('TracksRepository', function(apiUrl, $http) {
    this.search = function (callback, text, limit) {
        var params = {'where': JSON.stringify({'$text': {'$search': text}})};
        if (limit != null ) {
            params['max_results'] = limit;
        }

        $http.get(apiUrl + '/tracks/', {'params': params}).success(function(data){
               callback (data);
        });
    }
    this.getTrack = function (callback, id) {
        $http.get(apiUrl + '/tracks/' + id).success(function(data){
               callback (data);
        });
    }
    this.getStream = function(callback, id) {
        return callback(apiUrl + '/tracks/stream/' + id);
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
