    'use strict';
    var module = angular.module('play.controller', ['play.services']);
    module.controller('LoginController', ['$scope', '$location', 'MeRepository', 'MeService', function ($scope, $location, MeRepository, MeService) {
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

                }
            );
            return false;
        };
        resetForm();
    }]);
