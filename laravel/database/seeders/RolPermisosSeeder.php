<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class RolPermisosSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('rol_permisos')->truncate();

        DB::table('rol_permisos')->insert([
            [
                'rol_id' => DB::table('roles')->where('nombre_rol', 'Administrador')->value('id_rol'),
                'permiso_id' => DB::table('permisos')->where('nombre_permiso', 'ver_dashboard')->value('id_permiso')
            ],
            [
                'rol_id' => DB::table('roles')->where('nombre_rol', 'Administrador')->value('id_rol'),
                'permiso_id' => DB::table('permisos')->where('nombre_permiso', 'gestionar_usuarios')->value('id_permiso')
            ],
            [
                'rol_id' => DB::table('roles')->where('nombre_rol', 'Administrador')->value('id_rol'),
                'permiso_id' => DB::table('permisos')->where('nombre_permiso', 'gestionar_datos')->value('id_permiso')
            ],
            [
                'rol_id' => DB::table('roles')->where('nombre_rol', 'Administrador')->value('id_rol'),
                'permiso_id' => DB::table('permisos')->where('nombre_permiso', 'ver_reportes')->value('id_permiso')
            ]
        ]);
    }
}
