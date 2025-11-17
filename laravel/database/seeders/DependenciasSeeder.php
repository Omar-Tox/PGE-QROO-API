<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use App\Models\Dependencia;

class DependenciasSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE dependencias CASCADE');

        // 1. Dependencia Global (ID 1) - LA MÁS IMPORTANTE
        Dependencia::create([
            'id_dependencia' => 1,
            'nombre_dependencia' => 'Sistema PGE-QROO (Global)',
            'sector_id' => null, // O crea un Sector "Administración" si lo prefieres
        ]);

        // 2. Dependencia de Prueba (ID 2)
        Dependencia::create([
            'id_dependencia' => 2,
            'nombre_dependencia' => 'Secretaría de Finanzas',
            'sector_id' => null,
        ]);
        
        // 3. Otra dependencia de prueba (ID 3)
        Dependencia::create([
            'id_dependencia' => 3,
            'nombre_dependencia' => 'Secretaría de Educación',
            'sector_id' => null,
        ]);

        // Reiniciamos la secuencia para que la próxima dependencia creada sea la 4
        // (Sintaxis de PostgreSQL)
        DB::statement("SELECT setval(pg_get_serial_sequence('dependencias', 'id_dependencia'), (SELECT MAX(id_dependencia) FROM dependencias))");
    }
}
