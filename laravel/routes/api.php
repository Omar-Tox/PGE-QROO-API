<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\DependenciaController;

//----- RUTAS DEL SISTEMA -----

//Endpoint de nicio de sesion 
Route::post('/login', [AuthController::class, 'login']);

//----- RUTAS PROTEGIDAS (NO TOCAR) -----
// Todas las rutas dentro de este grupo requerirán un token válido

Route::middleware('auth:sanctum')->group(function () {
    
    //Obtener los datos del usuario logeado
    Route::get('/auth/me', [AuthController::class, 'me']);

    //Cerrar sesion
    Route::post('/logout', [AuthController::class, 'logout']);

    //Rutas de dependencias
    Route::apiResource('dependencias', DependenciaController::class);
});