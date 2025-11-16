<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class SectorSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('sector')->truncate();

        DB::table('sector')->insert([
            [
                'nombre_sector' => 'Salud',
                'descripcion' => ' Instituciones del sector salud del estado'
            ],
            [
                'nombre_sector' => 'Educación',
                'descripcion' => 'Instituciones educativas del estado'
            ],
            [
                'nombre_sector' => 'Seguridad',
                'descripcion' => ' Dependencias de seguridad pública'
            ],
            [
                'nombre_sector' => 'Administración Pública',
                'descripcion' => 'Oficinas administrativas y gubernamentales'
            ],
                        [
                'nombre_sector' => 'Infraestructura',
                'descripcion' => 'Organismos encargados de la gestión de obras públicas'
            ],

        ]);
    }
}
