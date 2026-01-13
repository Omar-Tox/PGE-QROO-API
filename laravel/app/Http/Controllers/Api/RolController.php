<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Rol;
use Illuminate\Http\Request;

class RolController extends Controller
{

    /**
     * @OA\Get(
     *     path="/api/roles",
     *     tags={"Roles"},
     *     summary="Listar roles del sistema",
     *     description="Devuelve el catálogo completo de roles disponibles en el sistema.",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Response(
     *         response=200,
     *         description="Listado de roles",
     *         @OA\JsonContent(
     *             type="array",
     *             @OA\Items(
     *                 type="object",
     *                 @OA\Property(property="id_rol", type="integer", example=1),
     *                 @OA\Property(property="nombre", type="string", example="Administrador"),
     *                 @OA\Property(property="descripcion", type="string", example="Acceso total al sistema")
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
        $roles = Rol::all();

        return response()->json($roles);
    }
}