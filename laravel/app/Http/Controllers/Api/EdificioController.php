<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Dependencia;
use App\Models\Edificio;
use Illuminate\Support\Facades\Gate;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class EdificioController extends Controller
{

    use AuthorizesRequests;
    /**
     * @OA\Get(
     *     path="/api/dependencias/{dependencia}/edificios",
     *     tags={"Edificios"},
     *     summary="Listar edificios de una dependencia",
     *     description="Devuelve todos los edificios asociados a una dependencia específica.",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="dependencia",
     *         in="path",
     *         required=true,
     *         description="ID de la dependencia",
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\Response(
     *         response=200,
     *         description="Lista de edificios",
     *         @OA\JsonContent(
     *             type="array",
     *             @OA\Items(
     *                 @OA\Property(property="id_edificio", type="integer", example=10),
     *                 @OA\Property(property="nombre_edificio", type="string", example="Edificio Central"),
     *                 @OA\Property(property="direccion", type="string", example="Av. Principal 123"),
     *                 @OA\Property(property="latitud", type="number", format="float", example=18.5001),
     *                 @OA\Property(property="longitud", type="number", format="float", example=-88.3002)
     *             )
     *         )
     *     ),
     *
     *     @OA\Response(response=403, description="No autorizado"),
     *     @OA\Response(response=404, description="Dependencia no encontrada")
     * )
     */
    public function index(Dependencia $dependencia)
    {
        // Autorizar si el usuario puede 'ver-edificios' de ESTA dependencia
        $this->authorize('ver-edificios', $dependencia);

        // Devolver los edificios de esa dependencia
        return response()->json($dependencia->edificios);
    }

    /**
     * @OA\Post(
     *     path="/api/dependencias/{dependencia}/edificios",
     *     tags={"Edificios"},
     *     summary="Crear edificio",
     *     description="Crea un nuevo edificio dentro de una dependencia.",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="dependencia",
     *         in="path",
     *         required=true,
     *         description="ID de la dependencia",
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\RequestBody(
     *         required=true,
     *         @OA\JsonContent(
     *             required={"nombre_edificio"},
     *             @OA\Property(property="nombre_edificio", type="string", example="Edificio Norte"),
     *             @OA\Property(property="direccion", type="string", example="Calle 10 #45"),
     *             @OA\Property(property="latitud", type="number", format="float", example=19.4326),
     *             @OA\Property(property="longitud", type="number", format="float", example=-99.1332),
     *             @OA\Property(property="caracteristicas", type="string", example="3 niveles, oficinas administrativas")
     *         )
     *     ),
     *
     *     @OA\Response(
     *         response=201,
     *         description="Edificio creado",
     *         @OA\JsonContent(
     *             @OA\Property(property="id_edificio", type="integer", example=15),
     *             @OA\Property(property="nombre_edificio", type="string", example="Edificio Norte")
     *         )
     *     ),
     *
     *     @OA\Response(response=403, description="No autorizado"),
     *     @OA\Response(response=422, description="Datos inválidos")
     * )
     */
    public function store(Request $request, Dependencia $dependencia)
    {
        /**
         * Autorizar si el usuario puede crear un nuevo edificio
         * para su dependencia
         */ 

        $this->authorize('crear-edificio', $dependencia);

        $validatedData = $request->validate([
            'nombre_edificio' => 'required|string|max:255',
            'direccion' => 'nullable|string|max:500',
            'latitud' => 'nullable|numeric|between:-90,90',
            'longitud' => 'nullable|numeric|between:-180,180',
            'caracteristicas' => 'nullable|string|max:500',
        ]);

        $edificio = $dependencia->edificios()->create($validatedData);

        return response()->json($edificio, 201);
    }

    /**
     * @OA\Put(
     *     path="/api/edificios/{edificio}",
     *     tags={"Edificios"},
     *     summary="Actualizar edificio",
     *     description="Actualiza los datos de un edificio existente.",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="edificio",
     *         in="path",
     *         required=true,
     *         description="ID del edificio",
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\RequestBody(
     *         @OA\JsonContent(
     *             @OA\Property(property="nombre_edificio", type="string", example="Edificio Renovado"),
     *             @OA\Property(property="direccion", type="string", example="Av. Reforma 100"),
     *             @OA\Property(property="latitud", type="number", format="float"),
     *             @OA\Property(property="longitud", type="number", format="float"),
     *             @OA\Property(property="caracteristicas", type="string", example="Paneles solares instalados")
     *         )
     *     ),
     *
     *     @OA\Response(response=200, description="Edificio actualizado"),
     *     @OA\Response(response=403, description="No autorizado"),
     *     @OA\Response(response=404, description="Edificio no encontrado"),
     *     @OA\Response(response=422, description="Datos inválidos")
     * )
     */
    public function update(Request $request, Edificio $edificio)
    {
        $this->authorize('actualizar-edificio', $edificio);

        $validatedData = $request->validate([
            'nombre_edificio' => 'sometimes|required|string|max:255',
            'direccion' => 'nullable|string|max:500',
            'latitud' => 'nullable|numeric|between:-90,90',
            'longitud' => 'nullable|numeric|between:-180,180',
            'caracteristicas' => 'nullable|string',
        ]);

        $edificio->update($validatedData);
        return response()->json($edificio);
    }

    /**
     * @OA\Delete(
     *     path="/api/edificios/{edificio}",
     *     tags={"Edificios"},
     *     summary="Eliminar edificio",
     *     description="Elimina un edificio del sistema.",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="edificio",
     *         in="path",
     *         required=true,
     *         description="ID del edificio",
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\Response(
     *         response=200,
     *         description="Edificio eliminado",
     *         @OA\JsonContent(
     *             @OA\Property(property="message", type="string", example="Edificio eliminado")
     *         )
     *     ),
     *
     *     @OA\Response(response=403, description="No autorizado"),
     *     @OA\Response(response=404, description="Edificio no encontrado")
     * )
     */
    public function destroy(Edificio $edificio)
    {
        $this->authorize('eliminar-edificio', $edificio);
        $edificio->delete();
        return response()->json([
            'message' => 'Edificio eliminado'
        ]);

    }
}
