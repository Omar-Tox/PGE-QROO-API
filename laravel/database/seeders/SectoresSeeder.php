<?php
namespace Database\Seeders;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class SectoresSeeder extends Seeder
{
    public function run(): void
    {
        // Limpiamos y reiniciamos secuencia para garantizar IDs 1-5
        DB::statement('TRUNCATE TABLE sector RESTART IDENTITY CASCADE');

        $sectores = [
            ['nombre_sector' => 'Educación', 'descripcion' => 'Instituciones educativas del estado'],
            ['nombre_sector' => 'Salud', 'descripcion' => 'Instituciones del sector salud'],
            ['nombre_sector' => 'Energía y Medio Ambiente', 'descripcion' => 'Dependencias relacionadas con energía y medio ambiente'],
            ['nombre_sector' => 'Infraestructura', 'descripcion' => 'Obras públicas e infraestructura gubernamental'],
            ['nombre_sector' => 'Finanzas y Administración', 'descripcion' => 'Gestión financiera del gobierno estatal'],
        ];

        foreach ($sectores as $sector) {
            DB::table('sector')->insert($sector);
        }
    }
}