<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Edificio;
use App\Models\ConsumoHistorico;
use Illuminate\Support\Facades\DB;

class ConsumoHistoricoSeeder extends Seeder
{
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE consumo_historico RESTART IDENTITY CASCADE');

        $edificios = Edificio::all();

        $this->command->info('Generando histórico de consumo para ' . $edificios->count() . ' edificios...');

        foreach ($edificios as $edificio) {
            for ($anio = 2022; $anio <= 2025; $anio++) {
                for ($mes = 1; $mes <= 12; $mes++) {
                    
                    $factorEstacional = ($mes >= 5 && $mes <= 9) ? 1.5 : 1.0;
                    
                    ConsumoHistorico::factory()->create([
                        'edificio_id' => $edificio->id_edificio,
                        'año' => $anio,
                        'mes' => $mes,
                        'consumo_kwh' => fake()->randomFloat(2, 2000, 4000) * $factorEstacional,
                        'costo_total' => fake()->randomFloat(2, 5000, 12000) * $factorEstacional,
                    ]);
                }
            }
        }
    }
}