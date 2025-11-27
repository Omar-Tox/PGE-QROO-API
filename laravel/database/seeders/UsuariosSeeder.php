<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use App\Models\User;
use App\Models\Rol;
use App\Models\Dependencia;


class UsuariosSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE usuarios CASCADE');
        DB::statement('TRUNCATE TABLE usuario_dependencia_roles CASCADE');

        // 1. Obtenemos los roles y dependencias que creamos
        $rolSuperAdmin = Rol::where('nombre_rol', 'Super Admin')->first();
        $rolAdminDep = Rol::where('nombre_rol', 'Admin Dependencia')->first();
        $rolLector = Rol::where('nombre_rol', 'Lector')->first();

        $depGlobal = Dependencia::find(1); // Sistema PGE-QROO (Global)
        $depFinanzas = Dependencia::find(2); // Secretaría de Finanzas
        $depEducacion = Dependencia::find(3); // Secretaría de Educación

        // 2. Creamos nuestro usuario de prueba (el que usas en Postman)
        $usuarioAdmin = User::create([
            'nombre_usuario' => 'admin_pge',
            'nombre' => 'Juan',
            'apellido' => 'Pérez',
            'email' => 'admin@pgeqroo.com',
            'contrasena' => 'password123',
            'activo' => true,
        ]);

        // 3. Asignamos los roles al usuario
        
        // Asignamos rol "Super Admin" en la dependencia "Global"
        $usuarioAdmin->roles()->attach($rolSuperAdmin->id_rol, [
            'dependencia_id' => $depGlobal->id_dependencia
        ]);
        
        // Asignamos rol "Admin Dependencia" para "Finanzas"
        $usuarioAdmin->roles()->attach($rolAdminDep->id_rol, [
            'dependencia_id' => $depFinanzas->id_dependencia
        ]);
        
        // Asignamos rol "Lector" para "Educación"
        $usuarioAdmin->roles()->attach($rolLector->id_rol, [
            'dependencia_id' => $depEducacion->id_dependencia
        ]);
    }
}
