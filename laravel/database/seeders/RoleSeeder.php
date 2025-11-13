<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class RoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('roles')->truncate();

        DB::table('roles')->insert([
            [
                'nombre_rol' => 'Administrador',
                'descripcion' => 'Acceso total al sistema'
            ],
            [
                'nombre_rol' => 'Analista',
                'descripcion' => 'Puede consultar datos y generar reportes'
            ],
            [
                'nombre_rol' => 'Operador',
                'descripcion' => 'Puede capturar información operativa'
            ],
            [
                'nombre_rol' => 'Visualizador',
                'descripcion' => 'Acceso de solo lectura'
            ]
        ]);
    }
}
