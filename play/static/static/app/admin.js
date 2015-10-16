(function() {
    'use strict';

    var app = angular.module('PlayAdminApp', ['play.services', 'ngRoute', 'ngResource', 'ui.bootstrap']);  // noqa
    app.value('apiUrl', '//localhost:8000/api');


    app.service('APIInterceptor', function() {
        var service = this;

        service.request = function(config) {
            if(typeof config.params !== 'undefined' && typeof config.params._etag !== 'undefined') {
                config.headers['If-Match'] = config.params._etag;
                delete config.params._etag;
            }
            return config;
        };

        service.responseError = function(response) {
            if (response.status === 401) {
                // console.log('user not authorized');
            }
            return response;
        };
    });

    app.config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
        $routeProvider.when('/directories', {
            templateUrl: 'templates/directories/index.html',
            controller: 'DirectoriesController',
            name: 'DirectoryList'
        }).when('/directories/new', {
            templateUrl: 'templates/directories/edit.html',
            controller: 'DirectoriesController',
            name: 'DirectoryCreate'
        }).when('/directories/:directoryId/edit', {
            templateUrl: 'templates/directories/edit.html',
            controller: 'DirectoriesController',
            name: 'DirectoryEdit'
        }).when('/directories/:directoryId', {
            templateUrl: 'templates/directories/user.html',
            controller: 'DirectoriesController',
            name: 'DirectoryView'
        }).when('/tracks', {
            templateUrl: 'templates/tracks.html',
            controller: 'TracksController'
        }).when('/users', {
            templateUrl: 'templates/users.html',
            controller: 'UserController',
            name: 'UserList'
        }).when('/users/new', {
            templateUrl: 'templates/users_edit.html',
            controller: 'UserController',
            name: 'UserCreate'
        }).when('/users/:userId', {
            templateUrl: 'templates/users_edit.html',
            controller: 'UserController',
            name: 'UserEdit'
        }).otherwise({
            redirectTo: '/directories'
        });

        $httpProvider.interceptors.push('APIInterceptor');
    }]);

    app.controller(
        'DirectoriesController', 
        ['$scope', 'DirectoryRepository', 'TrackRepository' ,'$route', '$location',
         function($scope, DirectoryRepository, TrackRepository, $route, $location){
             $scope.trackCount = 0;
             $scope.directory = {};
             $scope.directories = null;
             if ($route.current.$$route.name === 'DirectoryCreate') {
                 $scope.directory =  {};
             } else if ($route.current.$$route.name === 'DirectoryView') {
                 var directoryId = $route.current.params.directoryId;
                 $scope.directory =  DirectoryRepository.get(
                     directoryId,
                     function () {
                         $scope.tracks = TrackRepository.query({max_results:0, where: JSON.stringify({parents_directory: directoryId})});
                     });
             } else if ($route.current.$$route.name === 'DirectoryEdit') {
                 $scope.directory =  DirectoryRepository.get($route.current.params.directoryId);
             } else {
                 $scope.directories = DirectoryRepository.query({where: JSON.stringify({parent: null})});
             }
             $scope.go = function(directory, mode) {
                 if (typeof mode === 'undefined')
                     mode = '';
                 $location.path('/directories/' + directory._id + '/' + mode);
             };

             $scope.delete = function(directory) {
                 DirectoryRepository.delete(directory, function() {
                     $scope.directories._items.splice($scope.directories._items.indexOf(directory), 1);
                 });
             };

             $scope.save = function() {
                 if ($route.current.$$route.name === 'DirectoryEdit') {
                     DirectoryRepository.patch($scope.directory, {
                         name: $scope.directory.name,
                         path: $scope.directory.path
                     });
                 } else {
                     DirectoryRepository.create($scope.directory);
                 }
             };

             $scope.triggerRescan = function(directory) {
                 DirectoryRepository.triggerRescan(directory);
             };
         }]);

    app.controller('TracksController', ['$scope', 'TrackRepository', function($scope, TrackRepository){
        $scope.tracks = TrackRepository.query();

        $scope.setActiveState = function(track, state) {
            TrackRepository.patch(track, {'active': state}, function() {
                track.active = state;});
        };
        $scope.triggerRescan = function(track) {
            TrackRepository.triggerRescan(track);
        };
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

        $scope.save = function() {
            $scope.user.active = Boolean($scope.user.active);
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
            UserRepository.delete(user, function() {
                $scope.users._items.splice($scope.users._items.indexOf(user), 1);
            });
        };

        $scope.setActiveState = function(user, state) {
            UserRepository.patch(user, {'active': state}, function() {
                user.active = state;});
        };

        $scope.deleteRole = function(index) {
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
        };
    }]);







}());
