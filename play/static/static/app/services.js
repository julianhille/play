

    'use strict';
    var module = angular.module('play.services', ['ngResource']);
    module.value('apiUrl', '//localhost:8000/api');


    var createParams = function (params, merge) {
        var _params = angular.copy(params);
        if (typeof params !== 'undefined') {
            angular.extend(_params, merge);
            if (typeof _params.where !== 'undefined') {
                _params.where = JSON.stringify(_params.where);
            }
            if (typeof _params.embedded !== 'undefined') {
                _params.embedded = JSON.stringify(_params.embedded);
            }
        }
        return _params;
    }

    module.factory('TrackRepository', ['apiUrl', '$resource', '$http', function(apiUrl, $resource, $http) {
        var service = $resource(apiUrl + '/tracks/:trackId', {}, {
            query: {method:'GET', params:{trackId:''}},
            delete: {method: 'DELETE', cache: false},
            patch: {method: 'PATCH', cache: false},
            get: {method: 'GET', cache: false}
        });

        return {
            delete: function(track, success, error) {
                service.delete({trackId: track._id, _etag: track._etag}, success, error);
            },
            query: function(search, success, error)
            {

                return service.query(createParams(search), success, error);
            },
            get: function(trackId, success, error) {
                return service.get({trackId: trackId}, success, error);
            },
            patch: function (track, patch, success, error) {
                var success_callback = function(data) {
                    track._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch({trackId: track._id, _etag: track._etag}, patch, success_callback, error);
            },
            triggerRescan: function (track) {
                return $http.put(apiUrl + '/tracks/rescan', {_id: track._id});
            }
        };
    }]);


    module.factory('ArtistRepository', ['apiUrl', '$resource', function(apiUrl, $resource) {
        var service = $resource(apiUrl + '/artists/:artistId', {}, {
            query: {method:'GET', params:{artistId:''}},
            delete: {method: 'DELETE', cache: false},
            patch: {method: 'PATCH', cache: false},
            get: {method: 'GET', cache: false},
            create: {method: 'POST', cache: false}
        });

        return {
            delete: function(artist, success, error) {
                service.delete({artistId: artist._id, _etag: artist._etag}, success, error);
            },
            query: function(search, success, error)
            {
                return service.query(createParams(search), success, error);
            },
            get: function(artistId, success, error) {
                return service.get({artistId: artistId}, success, error);
            },
            patch: function (artist, patch, success, error) {
                var success_callback = function(data) {
                    artist._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch({artistId: artist._id, _etag: artist._etag}, patch, success_callback, error);
            },
            create: function (data, success, error) {
                return service.create({}, data, success, error );
            }
        };
    }]);


    module.factory('DirectoryRepository', ['apiUrl', '$resource', '$http', function(apiUrl, $resource, $http) {
        var service = $resource(apiUrl + '/directories/:directoryId', {}, {
            query: {method:'GET', params:{directoryId:''}},
            delete: {method: 'DELETE', cache: false},
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', cache: false}
        });

        return {
            delete: function(directory, success, error) {
                service.delete({directoryId: directory._id, _etag: directory._etag}, success, error);
            },
            query: function(search, success, error)
            {
                return service.query(createParams(search), success, error);
            },
            get: function(directoryId, success, error) {
                return service.get({directoryId: directoryId}, success, error);
            },
            patch: function (directory, patch, success, error) {
                var success_callback = function(data) {
                    directory._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch({directoryId: directory._id, _etag: directory._etag}, patch, success_callback, error);
            },
            create: function (data, success, error) {
                return service.create({}, data, success, error );
            },
            triggerRescan: function(directory) {
                return $http.put(apiUrl + '/directories/rescan', {_id: directory._id});
            }

        };
    }]);


    module.factory('UserRepository', ['apiUrl', '$resource', function(apiUrl, $resource) {
        var service = $resource(apiUrl + '/users/:userId', {}, {
            query: {method:'GET', params: {userId: ''}},
            delete: {method: 'DELETE', cache: false},
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', params: {userId:''}, cache: false}
        });

        return {
            delete: function(user, success, error) {
                return service.delete({userId: user._id, _etag: user._etag}, success, error);
            },
            query: function(search, success, error)
            {
                return service.query(createParams(search), success, error);
            },
            get: function(userId, success, error) {
                return service.get({userId: userId}, success, error);
            },
            patch: function (user, patch, success, error) {
                var success_callback = function(data){
                    user._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch(
                    {userId: user._id, _etag: user._etag}, patch, success_callback, error );
            },
            create: function (data, success, error) {
                return service.create({}, data, success, error );
            }
        };
    }]);


    module.service('MeRepository', ['apiUrl', '$http', '$resource', function (apiUrl, $http, $resource) {
        var service = $resource(apiUrl + '/me', {}, {
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', cache: false}
        });


        return {
            login:  function (username, password, remember, success, error) {
                $http.post(
                    apiUrl + '/me/login',
                    {
                        username: username,
                        password: password,
                        remember: remember
                    }).success(success || function() {}, error || function(){});
            },
            logout: function (success, error) {
                $http.post(apiUrl + '/me/logout', {}).then(success, error);
            },
            get: function (success, error) {
                return service.get({}, success, error);
            },
            patch: function (me, patch, success, error) {
                var success_callback = function(data){
                    me._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch(
                    {_etag: me._etag}, patch, success_callback, error );
            }
        };
    }]);


    module.service('PlaylistRepository', function (apiUrl, $resource) {




        /*
        this.getPlaylists = function (callback, where) {
            where = where ? '&where=' + JSON.stringify(where) : '';
            $http.get(apiUrl + '/playlists?embedded={"tracks": 1, "owner": 1}' + where).success(function (data) {
                callback(data);
            });
        };
        this.getUserPlaylists = function (callback, user_id) {
            this.getPlaylists(callback, {'owner': user_id});
        };
        this.getPlaylist = function (callback, id) {
            $http.get(apiUrl + '/playlists/' + id + '/?embedded={"tracks": 1, "owner": 1}').success(function (data) {
                callback(data);
            });
        };
        this.createPlaylist = function (callback, playlist_name) {
            $http.post(apiUrl + '/playlists/', {'name': playlist_name}).success(function (data) {
                callback(data);
            });

        };*/

        var service = $resource(apiUrl + '/playlists/:playlistId', {}, {
            query: {method:'GET', params: {playlistId: ''}},
            delete: {method: 'DELETE', cache: false},
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', cache: false}
        });

        return {
            delete: function(playlist, success, error) {
                return service.delete({playlistId: playlist._id, _etag: playlist._etag}, success, error);
            },
            query: function(search, success, error)
            {
                return service.query(createParams(search), success, error);
            },
            get: function(playlistId, params, success, error) {
                var _params = createParams(params, {playlistId: playlistId});
                return service.get(_params, success, error);
            },
            patch: function (playlist, patch, success, error) {
                var success_callback = function(data){
                    playlist._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch(
                    {playlistId: playlist._id, _etag: playlist._etag}, patch, success_callback, error );
            },
            create: function (data, success, error) {
                return service.create({}, data, success, error );
            }
        };
    });

    module.service('MeService', ['MeRepository', function(MeRepository) {
        var service = this;
        this.user = null;
        this.hasRole = function (role) {
            return service.isLoggedIn() && (service.user.roles || []).indexOf(role) > -1;
        };
        this.isAdmin = function () {
            return service.hasRole('admin');
        };
        this.isLoggedIn = function(vsr) {
            return service.user !== null;
        };
        this.logout = function() {
          MeRepository.logout(function() {
              service.user = null;
          });
        };
        this.init = function () {
            service.user = MeRepository.get();
        };
    }]);


    module.service('TrackService', ['TrackRepository', function (TrackRepository) {
        this.track = null;
        this.search = function (term) {
            return TrackRepository.query({'where': {'$text': {'$search': term}}});
        };
    }]);

    module.service('ArtistService', ['ArtistRepository', function (ArtistRepository) {
        this.artists = null;
        this.search = function (term) {
            return ArtistRepository.query({'where': {'$text': {'$search': term}}});
        };
    }]);
