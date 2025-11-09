<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;


class UsuariosSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('usuarios')->truncate();

        DB::table('usuarios')->insert([
            [
                'nombre_usuario'=>'admin',
                'nombre'=>'Administrador',
                'apellido'=>'General',
                'email'=>'admin@pge.qroo',
                'contrasena'=> bcrypt('admin123'),
            ]
        ]);
    }
}
