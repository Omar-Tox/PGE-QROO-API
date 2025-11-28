<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Services\NucleoDigitalService;
use App\Models\Dependencia;
use App\Models\Sector;
use Illuminate\Support\Facades\DB;

class SincronizarGobierno extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'db:sync-gobierno';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Descarga la información del Nucleo Digital y actualiza la base de datos';

    /**
     * Execute the console command.
     */
    public function handle(NucleoDigitalService $service)
    {
        $this->info('Iniciando la sincronización de datos...');

        // 1. Obtener datos del servicio
        $datos = $service->obtenerDatos();

        if (!$datos) {
            $this->error('Fallo al conectar con la API externa. Revisa los logs.');
            return;
        }

        DB::beginTransaction();

        try {
            /**
             * Sincronizar sectores
             */
            $this->info('Sincronizando sectores...');
            
            foreach($datos['sectores'] as $sectorExterno) {
                Sector::updateOrCreate(
                    ['nombre_sector' => $sectorExterno['nombre_sector']], // Busca por nombre
                    ['descripcion' => $sectorExterno['descripcion']]      // Actualiza descripción
                );
            }
            $this->info('Sectores sincronizados: '. count($datos['sectores']));

            /**
             * Sincronizar dependencias
             */
            $this->info('Sincronizando Dependencias...');
            $contadorDeps = 0;

            // Buscamos el sector por defecto "Administración Publica"
            // (Asegúrate de que este nombre exista en tu Seeder de Sectores o en la API)
            $sectorDefault = Sector::where('nombre_sector', 'Administración Publica')->first();
            $idSectorDefault = $sectorDefault ? $sectorDefault->id_sector : null;

            foreach ($datos['dependencias'] as $depExterna) {
                
                $dependencia = Dependencia::query()
                    ->where('nombre_dependencia', 'ILIKE', '%' . $depExterna['nombre_dependencia'] . '%')
                    ->orWhere(function($query) use ($depExterna) {
                        if (!empty($depExterna['acronimo'])) {
                            $query->where('nombre_dependencia', 'ILIKE', '%' . $depExterna['acronimo'] . '%');
                        }
                    })
                    ->first();

                // Si no existe, preparamos una nueva instancia
                if (!$dependencia) {
                    $dependencia = new Dependencia();
                    $dependencia->nombre_dependencia = $depExterna['nombre_dependencia'];
                    
                    // Solo asignamos el sector por defecto a las NUEVAS
                    // para no sobrescribir las que definiste manualmente en los Seeders
                    $dependencia->sector_id = $idSectorDefault;
                }

                // Aquí podrías actualizar campos adicionales si tu tabla los tuviera
                // Ej: $dependencia->titular = $depExterna['titular'];
                
                $dependencia->save();
                $contadorDeps++;
            }

            DB::commit();
            $this->info("Se sincronizaron $contadorDeps dependencias.");

        } catch (\Exception $e) {
            DB::rollBack();
            $this->error('Error durante la sincronización: ' . $e->getMessage());
        }
    }
}