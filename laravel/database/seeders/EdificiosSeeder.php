<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Dependencia;
use App\Models\Edificio;
use Illuminate\Support\Facades\DB;

class EdificiosSeeder extends Seeder
{
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE edificio RESTART IDENTITY CASCADE');

        
        $dependenciasReales = Dependencia::all();

        if ($dependenciasReales->isEmpty()) {
            $this->command->warn('No hay dependencias. Ejecuta "php artisan db:sync-gobierno" primero.');
            return;
        }

        $this->command->info('Generando edificios para ' . $dependenciasReales->count() . ' dependencias...');

        // 2. Para cada dependencia real, usamos el Factory para crearle edificios
        foreach ($dependenciasReales as $dependencia) {
            
            Edificio::factory()
                ->count(rand(2, 4))
                ->create([
                    'dependencia_id' => $dependencia->id_dependencia,
                    'nombre_edificio' => 'Oficinas ' . ($dependencia->acronimo ?? 'Centrales') . ' - ' . fake()->streetName(),
                ]);
        }
    }
}