<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class PresupuestosSeeder extends Seeder
{
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE presupuestos RESTART IDENTITY CASCADE');
        $data = [];
        // Dependencias ID 2 a 11
        for ($depId = 2; $depId <= 11; $depId++) {
            for ($anio = 2015; $anio <= 2024; $anio++) {
                for ($trim = 1; $trim <= 4; $trim++) {
                    $monto = rand(1500000 * 100, 8500000 * 100) / 100;
                    $data[] = [
                        'dependencia_id' => $depId,
                        'año' => $anio,
                        'trimestre' => $trim,
                        'monto_asignado' => $monto,
                    ];
                }
            }
        }
        foreach (array_chunk($data, 500) as $chunk) {
            DB::table('presupuestos')->insert($chunk);
        }
    }
}