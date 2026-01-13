<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\DB;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class UserController extends Controller
{
    use AuthorizesRequests;

    /**
     * @OA\Get(
     *     path="/api/usuarios",
     *     tags={"Usuarios"},
     *     summary="Listar usuarios",
     *     description="Devuelve todos los usuarios del sistema. Solo disponible para Super Admin.",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Response(
     *         response=200,
     *         description="Listado de usuarios",
     *         @OA\JsonContent(
     *             type="array",
     *             @OA\Items(ref="#/components/schemas/Usuario")
     *         )
     *     ),
     *     @OA\Response(response=403, description="No autorizado")
     * )
     */
    public function index()
    {
        $this->authorize('ver-lista-usuarios');

        // Devolver usuarios con sus roles y dependencias cargados
        $user = User::with(['roles', 'dependencias'])->get();

        return response()->json($user);
    }

    /**
     * @OA\Post(
     *     path="/api/usuarios",
     *     tags={"Usuarios"},
     *     summary="Crear usuario",
     *     security={{"sanctum":{}}},
     *
     *     @OA\RequestBody(
     *         required=true,
     *         @OA\JsonContent(
     *             required={"nombre_usuario","nombre","apellido","email","contrasena","asignaciones"},
     *             @OA\Property(property="nombre_usuario", type="string", example="jperez"),
     *             @OA\Property(property="nombre", type="string", example="Juan"),
     *             @OA\Property(property="apellido", type="string", example="Pérez"),
     *             @OA\Property(property="email", type="string", format="email"),
     *             @OA\Property(property="contrasena", type="string", format="password"),
     *             @OA\Property(
     *                 property="asignaciones",
     *                 type="array",
     *                 @OA\Items(ref="#/components/schemas/AsignacionRol")
     *             )
     *         )
     *     ),
     *
     *     @OA\Response(
     *         response=201,
     *         description="Usuario creado",
     *         @OA\JsonContent(ref="#/components/schemas/Usuario")
     *     ),
     *     @OA\Response(response=403, description="No autorizado")
     * )
     */
    public function store(Request $request)
    {
        $this->authorize('ver-lista-usuarios');

        $validatedData = $request->validate([
            'nombre_usuario' => 'required|string|unique:usuarios,nombre_usuario',
            'nombre' => 'required|string|max:100',
            'apellido' => 'required|string|max:100',
            'email' => 'required|email|unique:usuarios,email',
            'contrasena' => 'required|string|min:6',

            //validar los roles de asignación
            'asignaciones' => 'required|array',
            'asignaciones.*.rol_id' => 'required|exists:roles,id_rol',
            'asignaciones.*.dependencia_id' => 'required|exists:dependencias,id_dependencia'
        ]);

        //asegurar la integridad de los datos
        return DB::transaction(function () use ($validatedData) {
            //Crear el usuario

            $user = User::create([
                'nombre_usuario' => $validatedData['nombre_usuario'],
                'nombre' => $validatedData['nombre'],
                'apellido' => $validatedData['apellido'],
                'email' => $validatedData['email'],
                'contrasena' => $validatedData['contrasena'],
                'activo' => true
            ]);

            //Asignar roles y dependencias
            foreach($validatedData['asignaciones'] as $asignacion) {
                $user->roles()->attach($asignacion['rol_id'], [
                    'dependencia_id' => $asignacion['dependencia_id']
                ]);
            }
            return response()->json($user->load('roles'), 201);
        });
    }

    /**
     * @OA\Get(
     *     path="/api/usuarios/{id}",
     *     tags={"Usuarios"},
     *     summary="Ver usuario",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="id",
     *         in="path",
     *         required=true,
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\Response(
     *         response=200,
     *         description="Usuario encontrado",
     *         @OA\JsonContent(ref="#/components/schemas/Usuario")
     *     ),
     *     @OA\Response(response=404, description="Usuario no encontrado")
     * )
     */
    public function show(string $id)
    {
        $this->authorize('ver-lista-usuario');
        $user = User::where(['roles', 'dependencias'], findOrFail($id));
        return response()->json($user);
    }

    /**
     * @OA\Put(
     *     path="/api/usuarios/{id}",
     *     tags={"Usuarios"},
     *     summary="Actualizar usuario",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="id",
     *         in="path",
     *         required=true,
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\RequestBody(
     *         @OA\JsonContent(
     *             @OA\Property(property="nombre", type="string"),
     *             @OA\Property(property="apellido", type="string"),
     *             @OA\Property(property="email", type="string", format="email"),
     *             @OA\Property(property="contrasena", type="string"),
     *             @OA\Property(
     *                 property="asignaciones",
     *                 type="array",
     *                 @OA\Items(ref="#/components/schemas/AsignacionRol")
     *             )
     *         )
     *     ),
     *
     *     @OA\Response(
     *         response=200,
     *         description="Usuario actualizado",
     *         @OA\JsonContent(ref="#/components/schemas/Usuario")
     *     )
     * )
     */
    public function update(Request $request, string $id)
    {
        $this->authorize('ver-lista-usuarios');
        $user = User::findOrFail($id);
        
        $validatedData = $request->validate([
            'nombre' => 'sometimes|string|max:100',
            'apellido' => 'sometimes|string|max:100',
            'email' => 'sometimes|email|unique:usuarios,email,'.$id.',id_usuario',
            'contrasena' => 'nullable|string|min:6',
            //Actualizar roles (si es necesario)
            'asignaciones' => 'nullable|array',
            'asignaciones.*.rol_id' => 'exists:roles,id_rol',
            'asignaciones.*.dependencia_id' => 'exists:dependencias,id_dependencia',
        ]);

        DB::transaction(function () use ($user ,$validatedData) {
            //llenar los datos
            $user->fill($validatedData);

            //Validar si viene una contraseña nueva
            if(empty($validatedData['contrasena'])) {
                unset($user->contrasena);
            }

            $user->save();

            // Sincronizar Roles (Si se enviaron)
            if(isset($validatedData['asignaciones'])) {
                $syncData = [];

                foreach($validatedData['asignaciones'] as $asignacion) {
                    $user->roles()->detach();
                    foreach($validatedData['asignaciones'] as $asig) {
                        $user->roles()->attach($asig['rol_id'], ['dependencia_id' => $asig['dependencia_id']]);
                    }
                    break;
                }
            }
        });
        return response()->json($user->load('roles'));
    }

    /**
     * @OA\Delete(
     *     path="/api/usuarios/{id}",
     *     tags={"Usuarios"},
     *     summary="Desactivar usuario",
     *     security={{"sanctum":{}}},
     *
     *     @OA\Parameter(
     *         name="id",
     *         in="path",
     *         required=true,
     *         @OA\Schema(type="integer")
     *     ),
     *
     *     @OA\Response(
     *         response=200,
     *         description="Usuario desactivado"
     *     )
     * )
     */
    public function destroy(string $id)
    {
        $this->authorize('ver-lista-usuarios');
        $user = User::findOrFail($id);
        $user->activo = false;
        $user->save();

        return response()->json([
            'message' => 'Cuenta desactivada con éxito'
        ]);
    }
}
