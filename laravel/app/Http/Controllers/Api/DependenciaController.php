<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Dependencia;
use App\Models\Edificio;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class DependenciaController extends Controller
{
    use AuthorizesRequests;
    /**
     * @OA\Get(
     *     path="/api/dependencias",
     *     tags={"Dependencias"},
     *     summary="Listar dependencias",
     *     description="Lista dependencias visibles para el usuario autenticado.",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Response(
     *         response=200,
     *         description="Listado de dependencias",
     *         @OA\JsonContent(
     *             type="array",
     *             @OA\Items(
     *                 @OA\Property(property="id_dependencia", type="integer", example=1),
     *                 @OA\Property(property="nombre_dependencia", type="string", example="Secretaría de Educación"),
     *                 @OA\Property(property="edificios_count", type="integer", example=5)
     *             )
     *         )
     *     )
     * )
     */
    public function index(Request $request)
    {
        $user = $request->user();

        if($user->hasGlobalPermission('crear_dependencias')) {
            $dependencias = Dependencia::with('sector')
                                        ->withCount('edificios')
                                        ->get();

        }
        else {
            $dependencias = $user->dependencias()
                        ->with('edificios', 'sector')
                        ->withCount('edificios')
                        ->get();

        }
        return response()->json($dependencias);
    }

    /**
     * @OA\Post(
     *     path="/api/dependencias",
     *     tags={"Dependencias"},
     *     summary="Crear dependencia",
     *     security={{"sanctum":{}}},
     *
     *     @OA\RequestBody(
     *         required=true,
     *         @OA\JsonContent(
     *             required={"nombre_dependencia"},
     *             @OA\Property(property="nombre_dependencia", type="string", example="Nueva Secretaría"),
     *             @OA\Property(property="sector_id", type="integer", example=1)
     *         )
     *     ),
     *
     *     @OA\Response(response=201, description="Dependencia creada"),
     *     @OA\Response(response=403, description="No autorizado"),
     *     @OA\Response(response=422, description="Datos inválidos")
     * )
     */
    public function store(Request $request)
    {
        //Autorizamos la acción
        $this->authorize('crear-dependencia');

        $validatedData =$request->validate([
            'nombre_dependencia' => 'required|string|max:255|unique:dependencias',
            'sector_id' => 'nullable|integer|exists:sector,id_sector',
        ]);

        $dependencia = Dependencia::create($validatedData);

        return response()->json($dependencia, 201);
    }

    /**
     * @OA\Get(
     *     path="/api/dependencias/{dependencia}",
     *     tags={"Dependencias"},
     *     summary="Obtener dependencia especifica",
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
     *         description="Detalle de la dependencia",
     *         @OA\JsonContent(
     *             @OA\Property(property="id_dependencia", type="integer", example=1),
     *             @OA\Property(property="nombre_dependencia", type="string", example="Secretaría de Educación")
     *         )
     *     ),
     *
     *     @OA\Response(response=403, description="No autorizado"),
     *     @OA\Response(response=404, description="No encontrada")
     * )
     */
    public function show(Dependencia $dependencia)
    {
        // Autorizamos usando el Gate 'ver-dependencia'.
        // Laravel pasa automáticamente el usuario autenticado y la $dependencia
        $this->authorize('ver-dependencia', $dependencia);

        // Si pasa la autorización, mostrarlas
        $dependencia->load('edificios', 'presupuestos', 'sector')
                    ->loadCount('edificios');

        return response()->json($dependencia);
    }

    /**
     * @OA\Put(
     *     path="/api/dependencias/{dependencia}",
     *     tags={"Dependencias"},
     *     summary="Actualizar dependencia",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="dependencia",
     *         in="path",
     *         required=true,
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\RequestBody(
     *         @OA\JsonContent(
     *             @OA\Property(property="nombre_dependencia", type="string", example="Dependencia Actualizada"),
     *             @OA\Property(property="sector_id", type="integer", example=2)
     *         )
     *     ),
     *
     *     @OA\Response(response=200, description="Actualizada correctamente"),
     *     @OA\Response(response=403, description="No autorizado"),
     *     @OA\Response(response=422, description="Datos inválidos")
     * )
     */
    public function update(Request $request, Dependencia $dependencia)
    {
        // Autorizar la acción de actualizar
        $this->authorize('actualizar-dependencia', $dependencia);

        $validatedData = $request->validate([
            'nombre_dependencia' => 'sometimes|required|string|max:255|unique:dependencias,nombre_dependencia,' . $dependencia->id_dependencia . ',id_dependencia',
            'sector_id' => 'sometimes|integer|exists:sector,id_sector'
        ]);

        $dependencia->update($validatedData);

        return response()->json($dependencia);
    }

    /**
     * @OA\Delete(
     *     path="/api/dependencias/{dependencia}",
     *     tags={"Dependencias"},
     *     summary="Eliminar dependencia",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="dependencia",
     *         in="path",
     *         required=true,
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\Response(response=200, description="Eliminada correctamente"),
     *     @OA\Response(response=403, description="No autorizado")
     * )
     */
    public function destroy(Dependencia $dependencia)
    {
        // Autorizar la acción de eliminar
        $this->authorize('eliminar-dependencia', $dependencia);

        $dependencia->delete();

        return response()->json(
            ['message' => 'Dependencia eliminada con exito']
        );

    }
}
