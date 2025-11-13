<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class DependenciasSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('dependencias')->truncate();

        DB::table('dependencias')->insert([
            [
                'nombre_dependencia'=>'Secretaría de Salud de Quintana Roo', 
                'sector_id'=> DB::table('sector')->where('nombre_sector', 'Salud')->value('id_sector')
            ],
            [
                'nombre_dependencia'=>'Secretaría de Educación de Quintana Roo',
                'sector_id'=> DB::table('sector')->where('nombre_sector', 'Educación')->value('id_sector')
            ],
            [
                'nombre_dependencia'=>'Secretaría de Seguridad Pública del Estado',
                'sector_id'=> DB::table('sector')->where('nombre_sector', 'Seguridad')->value('id_sector')
            ],
            [
                'nombre_dependencia'=>'Secretaría de Finanzas y Planeación',
                'sector_id'=> DB::table('sector')->where('nombre_sector', ' Administración Pública')->value('id_sector')
            ],
        ]);
    }
}
