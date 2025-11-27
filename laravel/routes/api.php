<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\DependenciaController;
use App\Http\Controllers\Api\EdificioController;
use App\Http\Controllers\Api\PresupuestoController;
use App\Http\Controllers\Api\ConsumoController;
use App\Http\Controllers\Api\DashboardController;
use App\Http\Controllers\Api\ComparativaController;
use App\Http\Controllers\Api\UserController;
use App\Http\Controllers\Api\IntegracionController;


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

    //Rutas de dependencias (Ruta principal)

    Route::apiResource('dependencias', DependenciaController::class);

    /**
     * Subrutas
     * Rutas q dependen de dependencias como edificios o presupuestos
     * Ver y crear edificios & ver y asignar presupuestos
     * /api/dependencias/{dependencia}/edificios
     * /api/dependencias/{dependencia}/presupuestos
     */
    Route::get('/dependencias/{dependencia}/edificios', [EdificioController::class, 'index']);
    Route::post('/dependencias/{dependencia}/edificios', [EdificioController::class, 'store']);

    Route::get('/dependencias/{dependencia}/presupuestos', [PresupuestoController::class, 'index']);
    Route::post('/dependencias/{dependencia}/presupuestos', [PresupuestoController::class, 'store']);

    /**
     * Rutas para la importación de datos mediante el csv
     */

    Route::post('/consumos/carga-masiva', [ConsumoController::class, 'cargaMasiva']);

    /**
     * Rutas correspondientes al dashboard
     */
    Route::get('/dashboard', [DashboardController::class, 'index']);

    /**
     * Rutas para análisis
     */
    Route::get('/analisis/ranking-dependencias',[ComparativaController::class, 'index']);

    /**
     * Rutas Gestión de usuarios
     */
    Route::apiResource('usuarios', UserController::class);

    /**
     * Rutas para integración con Nucleo Digital
     */
    Route::get('integracion/gobierno',[IntegracionController::class, 'index']);
});