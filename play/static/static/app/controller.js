    'use strict';
    var module = angular.module('play.controller', ['play.services']);
    module.controller('LoginController', ['$scope', '$location', 'MeRepository', 'MeService', 'AUTH_EVENTS', '$rootScope', function LoginController($scope, $location, MeRepository, MeService, AUTH_EVENTS, $rootScope) {
        $scope.submit = submit;


        function submit() {
            MeRepository.login(
                $scope.name,
                $scope.password,
                $scope.remember,
                function successCallback(user) {
                    MeService.setUser(user);
                    resetForm();
                    $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
                }, function errorCallback(response) {
                    MeService.setUser(null);
                    $rootScope.$broadcast(AUTH_EVENTS.loginFailed, response);
                }
            );
            return false;
        };

        function resetForm() {
            $scope.name ='';
            $scope.password = '';
            $scope.remember = false;
        };

        resetForm();
    }]);
