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
        $this->info('Iniciando la sincronización de datos');

        $data = $service->obtenerDatos();

        if(!$data) {
            $this->error('Fallo al conectar con la API externa. Revisa los logs.');
            return;
        }

        DB::beginTransaction();

        try {
            // Sincronizar sectores
            $this->info('Sincronizando sectores...');
            $mapaSectores = [];
            
            foreach($data['sectores'] as $sectorExterno) {
                // Usamos updateOrCreate para no duplicar
                $sector = Sector::updateOrCreate(
                    ['nombre_sector' => $sectorExterno['nombre_sector']],
                    ['descripcion' => $sectorExterno['descripcion']]
                );
            }
            $this->info('Sectores sincronizados: '. count($data['sectores']));

            //Sincronizar dependencias
            $this->info('Sincronizando sectores...');
            $contadorDeps = 0;

            
            foreach($data['dependencias'] as $depExterna) {
                // IMPORTANTE: La API externa NO nos dice a qué sector pertenece cada dependencia.
                // Tendremos que dejarlo en null o asignar uno por defecto (ej. "Administración Pública").
                // O intentar adivinar por el nombre, pero es arriesgado.
                    
                // Por ahora, asignamos al sector "Administración Publica" (ID 5 en tu JSON) si existe, o null.
                $sectorDefault = Sector::where('nombre_sector', 'Administración Pública')->first();

                Dependencia::updateOrCreate(
                    ['nombre_dependencia' => $depExterna['nombre_dependencia']],
                    [
                        'sector_id' => $sectorDefault ? $sectorDefault->id_sector : null,
                    ]
                );
                $contadorDeps++;
                $this->info("¡Éxito! Se sincronizaron $contadorDeps dependencias.");
            }

            DB::commit();

        } catch (\Exception $e) {
            DB::rollBack();
            $this->error('Error durante la sincronización: ' . $e->getMessage());

        }
    }
}
