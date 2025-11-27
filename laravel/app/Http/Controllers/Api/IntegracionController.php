<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\NucleoDigitalService;
use Illuminate\Http\Request;

class IntegracionController extends Controller
{
    protected $nucleoService;

    public function __construct(NucleoDigitalService $nucleoService)
    {
        $this->nucleoService = $nucleoService;
    }

    /**
     * Obtiene los datos oficiales del Gobierno.
     */
    public function index()
    {
        // 1. Llamar al servicio
        $datos = $this->nucleoService->obtenerDatos();

        if (!$datos) {
            return response()->json([
                'message' => 'No se pudo conectar con el Núcleo Digital.'
            ], 502); // Bad Gateway
        }

        // 2. Retornar JSON limpio
        return response()->json($datos);
    }
}