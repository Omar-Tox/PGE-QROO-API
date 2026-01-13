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
    /*    
    * @OA\Get(
    *     path="/api/integracion/gobierno",
    *     tags={"Integración"},
    *     summary="Obtener datos oficiales del Gobierno",
    *     description="Consulta el servicio externo Núcleo Digital y devuelve los datos oficiales proporcionados por el Gobierno.",
    *     security={{"sanctum":{}}},
    *
    *     @OA\Response(
    *         response=200,
    *         description="Datos obtenidos correctamente",
    *         @OA\JsonContent(
    *             type="object",
    *             example={
    *                 "dependencias": {
    *                     {"id": 1, "nombre": "Secretaría de Educación"},
    *                     {"id": 2, "nombre": "Secretaría de Salud"}
    *                 },
    *                 "fecha_actualizacion": "2025-12-13T10:30:00Z"
    *             }
    *         )
    *     ),
    *
    *     @OA\Response(
    *         response=502,
    *         description="Error al conectar con el Núcleo Digital",
    *         @OA\JsonContent(
    *             @OA\Property(
    *                 property="message",
    *                 type="string",
    *                 example="No se pudo conectar con el Núcleo Digital."
    *             )
    *         )
    *     )
    * )
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