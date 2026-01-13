<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use App\Models\Rol;
use App\Models\Permiso;

class RolesSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE roles CASCADE');
        DB::statement('TRUNCATE TABLE rol_permisos CASCADE');

        // 1. Rol Super Administrador
        $superAdmin = Rol::create([
            'nombre_rol' => 'Super Admin',
            'descripcion' => 'Control total del sistema.'
        ]);

        // Asignamos todos los permisos globales
        $permisosGlobales = Permiso::whereIn('nombre_permiso', [
            'crear_dependencias', 
            'ver_usuarios_global', 
            'asignar_roles_global',
            'editar_dependencias', // Un Super Admin también puede editar/ver todo
            'eliminar_dependencias',
            'ver_presupuestos',
            'asignar_presupuestos',
            'ver_edificios',
            'crear_edificios',
            'cargar_consumos',
            'ver_dashboard'
        ])->pluck('id_permiso');
        $superAdmin->permisos()->attach($permisosGlobales);

        // 2. Rol Administrador de Dependencia
        $adminDep = Rol::create([
            'nombre_rol' => 'Admin Dependencia',
            'descripcion' => 'Control total de una dependencia específica.'
        ]);

        // Asignamos permisos de gestión de dependencia
        $permisosAdmin = Permiso::whereIn('nombre_permiso', [
            'editar_dependencias', // Editar su propia dependencia
            'ver_presupuestos',
            'asignar_presupuestos',
            'ver_edificios',
            'crear_edificios',
            'cargar_consumos',
            'ver_dashboard'
        ])->pluck('id_permiso');
        $adminDep->permisos()->attach($permisosAdmin); 

        // 3. Rol Lector
        $lector = Rol::create([
            'nombre_rol' => 'Lector',
            'descripcion' => 'Solo puede consultar información.'
        ]);
        // Asignamos permisos de solo lectura
        $permisosLector = Permiso::whereIn('nombre_permiso', [
            'ver_dashboard',
            'ver_presupuestos',
            'ver_edificios'
        ])->pluck('id_permiso');
        $lector->permisos()->attach($permisosLector);
    }
}
