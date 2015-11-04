    'use strict';
    var module = angular.module('play.controller', ['play.services']);
    module.controller('LoginController', ['$scope', '$location', 'MeRepository', 'MeService', 'AUTH_EVENTS', '$rootScope', function ($scope, $location, MeRepository, MeService, AUTH_EVENTS, $rootScope) {
        var resetForm = function() {
            $scope.name ='';
            $scope.password = '';
            $scope.remember = false;
        };
        $scope.submit = function () {
            MeRepository.login(
                $scope.name,
                $scope.password,
                $scope.remember,
                function(user) {
                    MeService.setUser(user);
                    resetForm();
                    $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);

                }, function(response) {
                    MeService.setUser(null);
                    $rootScope.$broadcast(AUTH_EVENTS.loginFailed, response);

                }
            );
            return false;
        };
        resetForm();
    }]);
