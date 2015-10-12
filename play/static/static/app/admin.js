
(function(){

    'use strict';

    var app = angular.module('PlayAdminApp', ['ngRoute', 'ngResource', 'ui.bootstrap'])
    app.value('apiUrl', '//localhost:8000/api');


    app.service('APIInterceptor', function($rootScope) {
        var service = this;

        service.request = function(config) {
            if(typeof config.params !== 'undefined' && typeof config.params._etag !== 'undefined') {
                config.headers['If-Match'] = config.params._etag;
                delete config.params._etag}
            return config;
        };

        service.responseError = function(response) {
            if (response.status === 401) {
                console.log('user logged out')
            }
            return response;
        };
    });

    app.config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
        $routeProvider.
          when('/directories', {
            templateUrl: 'templates/directories.html',
            controller: 'DirectoriesController'
        }).
          when('/tracks', {
            templateUrl: 'templates/tracks.html',
            controller: 'TracksController'
        }).
          when('/users', {
            templateUrl: 'templates/users.html',
            controller: 'UserController',
            name: 'UserList'
        }).
          when('/users/new', {
            templateUrl: 'templates/users_edit.html',
            controller: 'UserController',
            name: 'UserCreate'
        }).
         when('/users/:userId', {
            templateUrl: 'templates/users_edit.html',
            controller: 'UserController',
            name: 'UserEdit'
        }).
          otherwise({
            redirectTo: '/directories'
          });

          $httpProvider.interceptors.push('APIInterceptor');
    }]);

    app.controller('DirectoriesController', ['$scope', 'DirectoryRepository', '$uibModal', function($scope, DirectoryRepository, $uibModal){
        $scope.directories = DirectoryRepository.query({where: JSON.stringify({parent: null})});
        $scope.delete = function(directory) {
            DirectoryRepository.delete(directory,  function(value, responseHeaders) {
                $scope.directories._items.splice($scope.directories._items.indexOf(directory), 1);
            });
        };
    }]);

    app.controller('TracksController', ['$scope', 'TrackRepository', function($scope, TrackRepository){
        $scope.tracks = TrackRepository.query();
    }]);

    app.controller('UserController', ['$scope', '$route', '$location', 'UserRepository', function($scope, $route, $location, UserRepository){
        $scope.form = {role: ''};
        if ($route.current.$$route.name === 'UserCreate')
        {
            $scope.user =  {roles: []};
        } else if ($route.current.$$route.name === 'UserEdit') {
            $scope.user =  UserRepository.get($route.current.params.userId);
        } else {
            $scope.users = UserRepository.query();
        }
        $scope.go = function(user) {
            $location.path('/users/' + user._id);
        };
        $scope.save = function($event) {
            console.log($event.isImmediatePropagationStopped(), $event.isImmediatePropagationStopped());
            $scope.user.active = Boolean($scope.user.active);
            console.log($event.srcElement, $event, 'meh');
            return false;
            if ($route.current.$$route.name === 'UserEdit') {
                UserRepository.patch($scope.user, {
                    name: $scope.user.name,
                    password: $scope.user.password,
                    active: $scope.user.active
                });
            } else {
                UserRepository.create($scope.user);
            }

        };
        $scope.delete = function(user) {
            UserRepository.delete(user, function(value, responseHeaders) {
                $scope.users._items.splice($scope.users._items.indexOf(user), 1);
            });
        };
        $scope.setActiveState = function(user, state) {
            UserRepository.patch(user, {'active': state}, function(data) {
                user.active = state;});
        };

        $scope.deleteRole = function(index) {
            console.log(index);
            $scope.user.roles.splice(index, 1);
        };
        $scope.addRole = function ($event) {

            if ($event.keyCode === 13)
            {
                $event.preventDefault();
                $event.stopImmediatePropagation();
                $event.stopPropagation();
                if ($scope.user.roles.indexOf($scope.form.role) == -1)
                    $scope.user.roles.push($scope.form.role);
                return false;
            }
        }
    }]);


   app.factory('UserRepository', ['apiUrl', '$resource', '$http', function(apiUrl, $resource, $http) {
        var service = $resource(apiUrl + '/users/:userId', {}, {
            query: {method:'GET', params:{userId: ''}, },
            delete: {method: 'DELETE', cache: false},
            get: {method: 'GET', cache: false},
            patch: {method: 'PATCH', cache: false},
            create: {method: 'POST', params: {userId:''}, cache: false},
        });

        return {
            delete: function(user, success, error) {
                return service.delete({userId: user._id, _etag: user._etag}, success, error);
            },
            query: function(search, success, error)
            {
                return service.query(search);
            },
            get: function(userId, success, error) {
                return service.get({userId: userId});
            },
            patch: function (user, patch, success, error) {
                var success_callback = function(data){
                    user._etag = data._etag;
                    if (typeof success !== 'undefined' )
                        success(data);
                }
                return service.patch(
                    {userId: user._id, _etag: user._etag}, patch, success_callback, error );
            },
            create: function (data, success, error) {
                return service.create({}, data, success, error );
            }
        }
    }]);

   app.factory('DirectoryRepository', ['apiUrl', '$resource', '$http', function(apiUrl, $resource, $http) {
        var service = $resource(apiUrl + '/directories/:directoryId', {}, {
            query: {method:'GET', params:{directoryId:''}},
            delete: {method: 'DELETE', cache: false},
            patch: {method: 'PATCH', cache: false},
        });

        return {
            delete: function(directory, success, error) {
                service.delete({directoryId: directory._id, _etag: directory._etag}, success, error)
            },
            query: function(search, success, error)
            {
                return service.query(search);
            },
            get: function(directoryId, sucess, error) {
                return service.get({directoryId: directory._id});
            },
            patch: function (directory, patch, success, error) {
                return service.patch({directoryId: directory._id});
            }
        }
    }]);

    app.factory('TrackRepository', ['apiUrl', '$resource', '$http', function(apiUrl, $resource, $http) {
        var service = $resource(apiUrl + '/tracks/:trackId', {}, {
            query: {method:'GET', params:{trackId:''}},
            delete: {method: 'DELETE', cache: false},
            patch: {method: 'PATCH', cache: false},
            get: {method: 'GET', cache: false}
        });

        return {
            delete: function(track, success, error) {
                service.delete({trackId: track._id, _etag: track._etag}, success, error)
            },
            query: function(search, success, error)
            {
                return service.query(search);
            },
            get: function(trackId, success, error) {
                return service.get({track: trackId}, success, error);
            },
            patch: function (user, patch, success, error) {
                return service.patch({track: track._id}, patch, success, error);
            }
        }
    }]);

}());