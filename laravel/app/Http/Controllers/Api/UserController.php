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
     * Lista todos los usuarios del sistema
     * unicamente para el superAdmin
     */
    public function index()
    {
        $this->authorize('ver-lista-usuarios');

        // Devolver usuarios con sus roles y dependencias cargados
        $user = User::with(['roles', 'dependencias'])->get();

        return response()->json($user);
    }

    /**
     * Crear un nuevo usuario.
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
     * Display the specified resource.
     */
    public function show(string $id)
    {
        $this->authorize('ver-lista-usuario');
        $user = User::where(['roles', 'dependencias'], findOrFail($id));
        return response()->json($user);
    }

    /**
     * Update the specified resource in storage.
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
     * Desactiva un usuario (Soft Delete lógico)..
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
