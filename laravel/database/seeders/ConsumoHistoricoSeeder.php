<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class ConsumoHistoricoSeeder extends Seeder
{
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE consumo_historico RESTART IDENTITY CASCADE');
        $data = [];
        // Edificios ID 1 a 10 (Creados en EdificiosSeeder)
        for ($edifId = 1; $edifId <= 10; $edifId++) {
            for ($anio = 2015; $anio <= 2025; $anio++) {
                for ($mes = 1; $mes <= 12; $mes++) {
                    $consumo = rand(3000 * 100, 38000 * 100) / 100;
                    $costo = round($consumo * (rand(80, 260) / 100), 2);
                    $data[] = [
                        'edificio_id' => $edifId,
                        'año' => $anio,
                        'mes' => $mes,
                        'consumo_kwh' => $consumo,
                        'costo_total' => $costo,
                        'fuente_dato' => 'CFE',
                        'fecha_registro' => now(),
                    ];
                }
            }
        }
        foreach (array_chunk($data, 500) as $chunk) {
            DB::table('consumo_historico')->insert($chunk);
        }
    }
}