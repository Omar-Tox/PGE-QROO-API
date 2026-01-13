<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Dependencia;
use App\Models\Presupuesto;
use Illuminate\Support\Facades\DB;

class PresupuestosSeeder extends Seeder
{
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE presupuestos RESTART IDENTITY CASCADE');

        $dependencias = Dependencia::all();

        foreach ($dependencias as $dep) {
            for ($anio = 2020; $anio <= 2025; $anio++) {
                for ($trim = 1; $trim <= 4; $trim++) {
                    
                    Presupuesto::factory()->create([
                        'dependencia_id' => $dep->id_dependencia,
                        'año' => $anio,
                        'trimestre' => $trim,
                        'monto_asignado' => fake()->randomFloat(2, 100000 * ($anio - 2019), 500000 * ($anio - 2019)),
                    ]);
                }
            }
        }
    }
}