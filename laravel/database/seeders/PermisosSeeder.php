<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class PermisosSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('permisos')->truncate();

        DB::table('permisos')->insert([
            [
                'nombre_permiso' => 'ver_dashboard',
                'descripcion' => 'Acceso al panel principal'
            ],
            [
                'nombre_permiso' => 'gestionar_usuarios',
                'descripcion' => 'Crear y modificar usuarios'
            ],
            [
                'nombre_permiso' => 'gestionar_datos',
                'descripcion' => 'Registrar y procesar información energética'
            ],
            [
                'nombre_permiso' => 'ver_reportes',
                'descripcion' => 'Acceso a reportes y estadísticas'
            ],


        ]);
    }
}
