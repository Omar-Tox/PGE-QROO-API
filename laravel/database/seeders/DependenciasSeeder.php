<?php
namespace Database\Seeders;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class DependenciasSeeder extends Seeder
{
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE dependencias RESTART IDENTITY CASCADE');

        
        $dependencias = [
            ['id_dependencia' => 1, 'nombre_dependencia' => 'Sistema PGE-QROO (Global)', 'sector_id' => 5],
            ['id_dependencia' => 2, 'nombre_dependencia' => 'Secretaría de Educación de Quintana Roo (SEQ)', 'sector_id' => 1],
            ['id_dependencia' => 3, 'nombre_dependencia' => 'Universidad de Quintana Roo (UQROO)', 'sector_id' => 1],
            ['id_dependencia' => 4, 'nombre_dependencia' => 'Secretaría de Salud de Quintana Roo (SESA)', 'sector_id' => 2],
            ['id_dependencia' => 5, 'nombre_dependencia' => 'Comisión de Agua Potable y Alcantarillado (CAPA)', 'sector_id' => 3],
            ['id_dependencia' => 6, 'nombre_dependencia' => 'Secretaría de Obras Públicas (SEOP)', 'sector_id' => 4],
            ['id_dependencia' => 7, 'nombre_dependencia' => 'Secretaría de Finanzas y Planeación (SEFIPLAN)', 'sector_id' => 5],
            ['id_dependencia' => 8, 'nombre_dependencia' => 'Colegio de Bachilleres del Estado de Q. Roo (COBAQROO)', 'sector_id' => 1],
            ['id_dependencia' => 9, 'nombre_dependencia' => 'Secretaría de Medio Ambiente (SEMA)', 'sector_id' => 3],
            ['id_dependencia' => 10, 'nombre_dependencia' => 'Instituto de Infraestructura Física Educativa (IFEQROO)', 'sector_id' => 4],
            ['id_dependencia' => 11, 'nombre_dependencia' => 'Servicios Estatales de Salud Mental (SESA-Mental)', 'sector_id' => 2],
        ];

        foreach ($dependencias as $dep) {
            DB::table('dependencias')->insert($dep);
        }
        
        DB::statement("SELECT setval('dependencias_id_dependencia_seq', (SELECT MAX(id_dependencia) FROM dependencias))");
    }
}