<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use App\Models\User;
use App\Models\Rol;
use App\Models\Dependencia;

class UsuariosSeeder extends Seeder
{
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE usuarios RESTART IDENTITY CASCADE');
        DB::statement('TRUNCATE TABLE usuario_dependencia_roles RESTART IDENTITY CASCADE');

        // 1. Crear Usuario Admin
        $usuarioAdmin = User::create([
            'nombre_usuario' => 'admin_pge',
            'nombre' => 'Juan',
            'apellido' => 'Pérez',
            'email' => 'admin@pgeqroo.com',
            'contrasena' => 'password123',
            'activo' => true,
        ]);

        // 2. Obtener rol Super Admin
        $rolSuperAdmin = Rol::where('nombre_rol', 'Super Admin')->first();

        // 3. Asignar este usuario a TODAS las dependencias existentes
        $todasLasDependencias = Dependencia::all();

        foreach ($todasLasDependencias as $dep) {
            $usuarioAdmin->roles()->attach($rolSuperAdmin->id_rol, [
                'dependencia_id' => $dep->id_dependencia
            ]);
        }
    }
}