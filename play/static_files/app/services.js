

    'use strict';
    var module = angular.module('play.services', ['ngResource']);
    module.value('apiUrl', '//localhost:8000/api');
    module.constant('AUTH_EVENTS', {
        loginSuccess: 'auth-login-success',
        loginFailed: 'auth-login-failed',
        logoutSuccess: 'auth-logout-success',
        notAuthenticated: 'auth-not-authenticated',
        notAuthorized: 'auth-not-authorized'
    });

    module.factory('AuthInterceptor', ['$rootScope', 'AUTH_EVENTS', function AuthInterceptor($rootScope, AUTH_EVENTS) {
        return {
            responseError: function responseError(response) {
                $rootScope.$broadcast({
                    401: AUTH_EVENTS.notAuthenticated,
                    403: AUTH_EVENTS.notAuthorized
                }[response.status], response);
                throw response;
            }
        };
    }]);

    module.factory('EtagInterceptor', function EtagInterceptor() {

        return {
            request: function request(config) {
                if(typeof config.params !== 'undefined' && typeof config.params._etag !== 'undefined') {
                    config.headers['If-Match'] = config.params._etag;
                    delete config.params._etag;
                }
                return config;
            }
        };
    });

    var createParams = function createParams(params, merge) {
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
    };

    module.factory('TrackRepository', ['apiUrl', '$resource', '$http', function TrackRepository(apiUrl, $resource, $http) {
        var service = $resource(apiUrl + '/tracks/:trackId', {}, {
            query: {method:'GET', params:{trackId:''}},
            delete: {method: 'DELETE', cache: false},
            patch: {method: 'PATCH', cache: false},
            get: {method: 'GET', cache: false}
        });

        return {
            delete: function remove(track, success, error) {
                service.delete({trackId: track._id, _etag: track._etag}, success, error);
            },
            query: function query(search, success, error)
            {

                return service.query(createParams(search), success, error);
            },
            get: function get(trackId, success, error) {
                return service.get({trackId: trackId}, success, error);
            },
            patch: function patch(track, patch, success, error) {
                var success_callback = function success_callback(data) {
                    track._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch({trackId: track._id, _etag: track._etag}, patch, success_callback, error);
            },
            triggerRescan: function triggerRescan(track) {
                return $http.put(apiUrl + '/tracks/rescan', {_id: track._id});
            }
        };
    }]);


    module.factory('ArtistRepository', ['apiUrl', '$resource', function ArtistRepository(apiUrl, $resource) {
        var service = $resource(apiUrl + '/artists/:artistId', {}, {
            query: {method:'GET', params:{artistId:''}},
            delete: {method: 'DELETE', cache: false},
            patch: {method: 'PATCH', cache: false},
            get: {method: 'GET', cache: false},
            create: {method: 'POST', cache: false}
        });

        return {
            delete: function remove(artist, success, error) {
                service.delete({artistId: artist._id, _etag: artist._etag}, success, error);
            },
            query: function query(search, success, error)
            {
                return service.query(createParams(search), success, error);
            },
            get: function get(artistId, success, error) {
                return service.get({artistId: artistId}, success, error);
            },
            patch: function patch(artist, patch, success, error) {
                var success_callback = function(data) {
                    artist._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch({artistId: artist._id, _etag: artist._etag}, patch, success_callback, error);
            },
            create: function create(data, success, error) {
                return service.create({}, data, success, error );
            }
        };
    }]);


    module.factory('DirectoryRepository', ['apiUrl', '$resource', '$http', function DirectoryRepository(apiUrl, $resource, $http) {
        var service = $resource(apiUrl + '/directories/:directoryId', {}, {
            query: {method:'GET', params:{directoryId:''}},
            delete: {method: 'DELETE', cache: false},
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', cache: false}
        });

        return {
            delete: function remove(directory, success, error) {
                service.delete({directoryId: directory._id, _etag: directory._etag}, success, error);
            },
            query: function query(search, success, error)
            {
                return service.query(createParams(search), success, error);
            },
            get: function get(directoryId, success, error) {
                return service.get({directoryId: directoryId}, success, error);
            },
            patch: function patch(directory, patch, success, error) {
                var success_callback = function(data) {
                    directory._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch({directoryId: directory._id, _etag: directory._etag}, patch, success_callback, error);
            },
            create: function create(data, success, error) {
                return service.create({}, data, success, error );
            },
            triggerRescan: function triggerRescan(directory) {
                return $http.put(apiUrl + '/directories/rescan', {_id: directory._id});
            }

        };
    }]);


    module.factory('UserRepository', ['apiUrl', '$resource', function UserRepository(apiUrl, $resource) {
        var service = $resource(apiUrl + '/users/:userId', {}, {
            query: {method:'GET', params: {userId: ''}},
            delete: {method: 'DELETE', cache: false},
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', params: {userId:''}, cache: false}
        });

        return {
            delete: function remove(user, success, error) {
                return service.delete({userId: user._id, _etag: user._etag}, success, error);
            },
            query: function query(search, success, error)
            {
                return service.query(createParams(search), success, error);
            },
            get: function get(userId, success, error) {
                return service.get({userId: userId}, success, error);
            },
            patch: function patch(user, patch, success, error) {
                var success_callback = function(data){
                    user._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch(
                    {userId: user._id, _etag: user._etag}, patch, success_callback, error );
            },
            create: function create(data, success, error) {
                return service.create({}, data, success, error );
            }
        };
    }]);


    module.service('MeRepository', ['apiUrl', '$http', '$resource', function MeRepository(apiUrl, $http, $resource) {
        var service = $resource(apiUrl + '/me', {}, {
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', cache: false}
        });


        return {
            login: function login(username, password, remember, success, error) {
                $http.post(
                    apiUrl + '/me/login',
                    {
                        username: username,
                        password: password,
                        remember: remember
                    }).success(success || function() {}, error || function(){});
            },
            logout: function logout(success, error) {
                $http.post(apiUrl + '/me/logout', {}).then(success, error);
            },
            get: function get(success, error) {
                return service.get({}, success, error);
            },
            patch: function patch(me, patch, success, error) {
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

        var service = $resource(apiUrl + '/playlists/:playlistId', {}, {
            query: {method:'GET', params: {playlistId: ''}},
            delete: {method: 'DELETE', cache: false},
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', cache: false}
        });

        return {
            delete: function remove(playlist, success, error) {
                return service.delete({playlistId: playlist._id, _etag: playlist._etag}, success, error);
            },
            query: function query(search, success, error)
            {
                return service.query(createParams(search), success, error);
            },
            get: function get(playlistId, params, success, error) {
                var _params = createParams(params, {playlistId: playlistId});
                return service.get(_params, success, error);
            },
            patch: function patch(playlist, patch, success, error) {
                var success_callback = function(data){
                    playlist._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                };
                return service.patch(
                    {playlistId: playlist._id, _etag: playlist._etag}, patch, success_callback, error );
            },
            create: function create(data, success, error) {
                return service.create({}, data, success, error );
            }
        };
    });

    module.service('MeService', ['$rootScope', 'MeRepository', 'AUTH_EVENTS', function MeService($rootScope, MeRepository, AUTH_EVENTS) {
        var service = this;
        this.user = null;
        this.hasRole = function hasRole(role) {
            return service.isLoggedIn() && (service.user.roles || []).indexOf(role) > -1;
        };
        this.isAdmin = function isAdmin() {
            return service.hasRole('admin');
        };
        this.isLoggedIn = function isLoggedIn() {
            return !!service.user && !!service.user._id;
        };
        this.logout = function logout() {
            MeRepository.logout(function() {
                service.user = null;
                $rootScope.$broadcast(AUTH_EVENTS.logoutSuccess);
            });
        };
        this.setUser = function setUser(user) {
            service.user = user;
        };
        this.init = function init() {
            service.user = MeRepository.get(function successCallback() {
                $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
            });

        };
    }]);


    module.service('TrackService', ['TrackRepository', function TrackService(TrackRepository) {
        this.track = null;
        this.search = function search(term) {
            return TrackRepository.query({'where': {'$text': {'$search': term}}});
        };
    }]);


    module.service('ArtistService', ['ArtistRepository', function ArtistService(ArtistRepository) {
        this.artists = null;
        this.search = function search(term) {
            return ArtistRepository.query({'where': {'$text': {'$search': term}}});
        };
    }]);
