<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Dependencia;
use App\Models\Presupuesto;
use Illuminate\Support\Facades\Gate;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;


class PresupuestoController extends Controller
{
    use AuthorizesRequests;

    /**
     * @OA\Get(
     *     path="/api/dependencias/{dependencia}/presupuestos",
     *     tags={"Presupuestos"},
     *     summary="Listar presupuestos de una dependencia",
     *     security={{"sanctum":{}}},
     *     @OA\Parameter(
     *         name="dependencia",
     *         in="path",
     *         required=true,
     *         description="ID de la dependencia",
     *         @OA\Schema(type="integer")
     *     ),
     *     @OA\Response(
     *         response=200,
     *         description="Lista de presupuestos",
     *         @OA\JsonContent(
     *             type="array",
     *             @OA\Items(ref="#/components/schemas/Presupuesto")
     *         )
     *     ),
     *     @OA\Response(response=403, description="No autorizado")
     * )
     */
    public function index(Dependencia $dependencia)
    {
        // Autorizar si el usuario puede 'ver-presupuesto' de ESTA dependencia
        $this->authorize('ver-presupuestos', $dependencia);

        // Devolver los presupuestos de la dependencia por años
        return response()->json(
            $dependencia->presupuestos()
                        ->orderBy('año', 'desc')
                        ->orderBy('trimestre', 'desc')
                        ->get()
        );
    }

    /**
     * @OA\Post(
     *     path="/api/dependencias/{dependencia}/presupuestos",
     *     tags={"Presupuestos"},
     *     summary="Asignar presupuesto a una dependencia",
     *     security={{"sanctum":{}}},
     *     @OA\Parameter(
     *         name="dependencia",
     *         in="path",
     *         required=true,
     *         description="ID de la dependencia",
     *         @OA\Schema(type="integer")
     *     ),
     *     @OA\RequestBody(
     *         required=true,
     *         @OA\JsonContent(
     *             required={"año","trimestre","monto_asignado"},
     *             @OA\Property(property="año", type="integer", example=2025),
     *             @OA\Property(property="trimestre", type="integer", example=1),
     *             @OA\Property(property="monto_asignado", type="number", format="float", example=250000.75)
     *         )
     *     ),
     *     @OA\Response(
     *         response=201,
     *         description="Presupuesto creado",
     *         @OA\JsonContent(ref="#/components/schemas/Presupuesto")
     *     ),
     *     @OA\Response(response=409, description="Presupuesto duplicado"),
     *     @OA\Response(response=403, description="No autorizado")
     * )
     */
    public function store(Request $request, Dependencia $dependencia)
    {
        $this->authorize('asignar-presupuesto', $dependencia);

        $validatedData = $request->validate([
            'año' => 'required|integer|min:2020|max:2050',
            'trimestre' => 'required|integer|min:1|max:4',
            'monto_asignado' => 'required|numeric|min:0'
        ]);

        /**
         * Validar que los datos no esten duplicados
         */
        $exists = $dependencia->presupuestos()
                            ->where('año', $validatedData['año'])
                            ->where('trimestre', $validatedData['trimestre'])
                            ->exists();

        if($exists) {
            return response()->json(
                ['message' => 'Ya existe un presupuesto para este año o trimestre', 409]
            );
        }

        $presupuesto = $dependencia->presupuestos()->create($validatedData);
        
        return response()->json($presupuesto, 201);
    }
}
