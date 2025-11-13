<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class UsuarioDependenciaRolesSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('usuario_dependencia_roles')->truncate();

        DB::table('usuario_dependencia_roles')->insert([
            [
                'usuario_id' => DB::table('usuarios')->where('nombre_usuario', 'admin')->value('id_usuario'),
                'dependencia_id' => DB::table('dependencias')->where('nombre_dependencia', 'Secretaría de Finanzas y Planeación')->value('id_dependencia'),
                'rol_id' => DB::table('roles')->where('nombre_rol', 'Administrador')->value('id_rol')
            ]
        ]);
    }
}
