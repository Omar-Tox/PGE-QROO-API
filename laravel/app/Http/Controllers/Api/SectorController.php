<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Sector;
use Illuminate\Http\Request;

class SectorController extends Controller
{

    /**
     * @OA\Get(
     *     path="/api/sectores",
     *     tags={"Sectores"},
     *     summary="Listar sectores",
     *     description="Devuelve todos los sectores registrados junto con el número de dependencias asociadas.",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Response(
     *         response=200,
     *         description="Listado de sectores",
     *         @OA\JsonContent(
     *             type="array",
     *             @OA\Items(
     *                 type="object",
     *                 @OA\Property(property="id_sector", type="integer", example=1),
     *                 @OA\Property(property="nombre_sector", type="string", example="Sector Educativo"),
     *                 @OA\Property(property="dependencias_count", type="integer", example=8)
     *             )
     *         )
     *     ),
     *
     *     @OA\Response(
     *         response=401,
     *         description="No autenticado"
     *     )
     * )
     */
    public function index()
    {   
        $sectores = Sector::withCount('dependencias')->get();

        return response()->json($sectores);
    }
}