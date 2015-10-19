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
            templateUrl: 'templates/directories/view.html',
            controller: 'DirectoriesController',
            name: 'DirectoryView'
        }).when('/tracks', {
            templateUrl: 'templates/tracks.html',
            controller: 'TracksController'
        }).when('/users', {
            templateUrl: 'templates/users/index.html',
            controller: 'UserController',
            name: 'UserList'
        }).when('/users/new', {
            templateUrl: 'templates/users/edit.html',
            controller: 'UserController',
            name: 'UserCreate'
        }).when('/users/:userId', {
            templateUrl: 'templates/users/edit.html',
            controller: 'UserController',
            name: 'UserEdit'
        }).when('/artists/new', {
            templateUrl: 'templates/artists/edit.html',
            controller: 'ArtistController',
            name: 'ArtistNew'
        }).when('/artists', {
            templateUrl: 'templates/artists/index.html',
            controller: 'ArtistListController',
            name: 'ArtistList'
        }).when('/artists/:artistId', {
            templateUrl: 'templates/artists/view.html',
            controller: 'ArtistController',
            name: 'ArtistView'
        }).when('/artists/:artistId/edit', {
            templateUrl: 'templates/artists/edit.html',
            controller: 'ArtistController',
            name: 'ArtistEdit'
        }).otherwise({
            redirectTo: '/directories'
        });

        $httpProvider.interceptors.push('APIInterceptor');
    }]);

    app.controller(
        'DirectoriesController', 
        ['$scope', 'DirectoryRepository', 'TrackRepository' ,'$route',
         function($scope, DirectoryRepository, TrackRepository, $route){
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

    app.controller('ArtistController', ['$route', '$scope', 'ArtistRepository', function($route, $scope, ArtistRepository) {
        $scope.artist = {};
        if(['ArtistView', 'ArtistEdit'].indexOf($route.current.$$route.name) > -1) {
            $scope.artist = ArtistRepository.get($route.current.params.artistId);
        }
        $scope.save = function() {
            if ($scope.artist._id) {
                ArtistRepository.patch($scope.artist, {
                    name: $scope.artist.name,
                    realname: $scope.artist.realname,
                    profile: $scope.artist.profile,
                    aliases: $scope.artist.aliases,
                    namevariations: $scope.artist.namevariations
                });
            } else {
                ArtistRepository.create({
                    name: $scope.artist.name,
                    realname: $scope.artist.realname,
                    profile: $scope.artist.profile,
                    aliases: $scope.artist.aliases,
                    namevariations: $scope.artist.namevariations
                });
            }

        };
    }]);

    app.controller('ArtistListController', ['$scope', '$location', 'ArtistRepository', function($scope, $location, ArtistRepository){
        $scope.currentPage = 5;
        $scope.maxResults = 2;
        $scope.totalItems = 25;
        $scope.searchCriteria = [];
        $scope.search = {
            page: 1,
            max_results: 100,
            where: {}
        };

        $scope.criteriaForm = {
            field: 'search',
            value: ''
        };


        $scope.deleteCriteria = function (index) {
            $scope.searchCriteria.splice(index, 1);
            $scope.updateArtists();
        };

        $scope.updateArtists = function () {
            var search = angular.copy($scope.search);
            $scope.searchCriteria.forEach(function (criteria) {
                if (!(criteria.field in search.where)) {
                    search.where[criteria.field] = {'$in': []};
                }
                search.where[criteria.field]['$in'].push(criteria.value);
            });

            $scope.artists = ArtistRepository.query(search, function (data) {
                $scope.currentPage = data._meta.page;
                $scope.maxResults = data._meta.max_results;
                $scope.totalItems = data._meta.total;
                $scope.search.page = data._meta.page;
            });
        };

        $scope.addSearchCriteria = function () {
            if ($scope.criteriaForm.field && $scope.criteriaForm.value) {
                $scope.searchCriteria.push(
                    {
                        field: $scope.criteriaForm.field,
                        value: $scope.criteriaForm.value
                    });
                $scope.updateArtists();
            }
        };

        $scope.updateArtists();
    }]);



}());
