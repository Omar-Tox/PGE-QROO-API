<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use App\Models\Permiso;

class PermisosSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE permisos CASCADE');

        $permisos = [
            // Permisos Globales (Super Admin)
            ['nombre_permiso' => 'crear_dependencias', 'descripcion' => 'Permite crear nuevas dependencias en el sistema.'],
            ['nombre_permiso' => 'ver_usuarios_global', 'descripcion' => 'Permite ver y gestionar todos los usuarios del sistema.'],
            ['nombre_permiso' => 'asignar_roles_global', 'descripcion' => 'Permite asignar roles a cualquier usuario en cualquier dependencia.'],

            // Permisos de Dependencia (Admin de Dependencia)
            ['nombre_permiso' => 'editar_dependencias', 'descripcion' => 'Permite editar la información de una dependencia.'],
            ['nombre_permiso' => 'eliminar_dependencias', 'descripcion' => 'Permite eliminar una dependencia.'],
            ['nombre_permiso' => 'ver_presupuestos', 'descripcion' => 'Permite ver los presupuestos de una dependencia.'],
            ['nombre_permiso' => 'asignar_presupuestos', 'descripcion' => 'Permite asignar nuevos presupuestos a una dependencia.'],
            ['nombre_permiso' => 'ver_edificios', 'descripcion' => 'Permite ver los edificios de una dependencia.'],
            ['nombre_permiso' => 'crear_edificios', 'descripcion' => 'Permite añadir edificios a una dependencia.'],
            ['nombre_permiso' => 'cargar_consumos', 'descripcion' => 'Permite cargar consumos históricos (CSV/Excel) para una dependencia.'],
            
            // Permisos de Lector (Consulta)
            ['nombre_permiso' => 'ver_dashboard', 'descripcion' => 'Permite ver el dashboard de una dependencia.'],
        ];

        foreach($permisos as $permiso) {
            Permiso::create($permiso);
        }
    }
}
