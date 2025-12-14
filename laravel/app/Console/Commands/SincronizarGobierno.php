<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Services\NucleoDigitalService;
use App\Models\Dependencia;
use App\Models\Sector;
use App\Models\User;
use App\Models\Rol;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

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
    protected $description = 'Descarga datos del Núcleo Digital, sincroniza Dependencias, Sectores y crea Usuarios con los datos de la API.';

    /**
     * Execute the console command.
     */
    public function handle(NucleoDigitalService $service)
    {
        $this->info('Iniciando sincronización inteligente con el Gobierno...');

        $datos = $service->obtenerDatos();

        if (!$datos) {
            $this->error('Fallo al conectar con la API externa. Revisa los logs.');
            return;
        }

        DB::beginTransaction();

        try {
            // ---------------------------------------------------------
            // 1. SINCRONIZAR SECTORES
            // ---------------------------------------------------------
            $this->info('--- Sincronizando Sectores ---');
            foreach($datos['sectores'] as $sectorExterno) {
                Sector::updateOrCreate(
                    ['nombre_sector' => $sectorExterno['nombre_sector']], 
                    ['descripcion' => $sectorExterno['descripcion']]
                );
            }
            $this->info('Sectores actualizados.');

            // ---------------------------------------------------------
            // 2. SINCRONIZAR DEPENDENCIAS Y USUARIOS
            // ---------------------------------------------------------
            $this->info('--- Sincronizando Dependencias y Usuarios ---');
            
            $sectorDefault = Sector::where('nombre_sector', 'Administración Publica')->first();
            $idSectorDefault = $sectorDefault ? $sectorDefault->id_sector : null;
            
            // Buscamos el rol de "Admin Dependencia" (Asumimos ID 2 o buscamos por nombre)
            $rolAdminDep = Rol::where('nombre_rol', 'Admin Dependencia')->first();

            $contadorDeps = 0;
            $contadorUsers = 0;

            foreach ($datos['dependencias'] as $depExterna) {
                
                // A. CREAR O ACTUALIZAR DEPENDENCIA
                $dependencia = Dependencia::query()
                    ->where('nombre_dependencia', 'ILIKE', '%' . $depExterna['nombre_dependencia'] . '%')
                    ->orWhere(function($query) use ($depExterna) {
                        if (!empty($depExterna['acronimo'])) {
                            $query->where('nombre_dependencia', 'ILIKE', '%' . $depExterna['acronimo'] . '%');
                        }
                    })
                    ->first();

                if (!$dependencia) {
                    $dependencia = new Dependencia();
                    $dependencia->nombre_dependencia = $depExterna['nombre_dependencia'];
                    $dependencia->sector_id = $idSectorDefault;
                }
                
                $dependencia->save();
                $contadorDeps++;

                // B. CREAR USUARIO (TITULAR)
                // Solo si tenemos nombre de titular y un email válido
                if (!empty($depExterna['titular']) && !empty($depExterna['contacto']['email']) && $rolAdminDep) {
                    
                    // Separar Nombre y Apellido (Lógica simple: Primer espacio)
                    $nombreCompleto = trim($depExterna['titular']);
                    $partes = explode(' ', $nombreCompleto, 2);
                    $nombre = $partes[0];
                    $apellido = $partes[1] ?? 'Funcionario'; // Apellido por defecto si no hay

                    // Crear Usuario
                    $usuario = User::updateOrCreate(
                        ['email' => $depExterna['contacto']['email']], // Buscamos por email único
                        [
                            'nombre_usuario' => Str::slug($nombre . '.' . $apellido . rand(1,100)), // Generar user único
                            'nombre' => $nombre,
                            'apellido' => $apellido,
                            'contrasena' => 'password', // Mutator lo hasheará automáticamente
                            'activo' => true
                        ]
                    );

                    // Asignar Rol: Admin Dependencia PARA ESTA DEPENDENCIA
                    // Usamos syncWithoutDetaching para no borrarle otros roles si los tuviera
                    $usuario->roles()->syncWithoutDetaching([
                        $rolAdminDep->id_rol => ['dependencia_id' => $dependencia->id_dependencia]
                    ]);

                    $contadorUsers++;
                }
            }

            DB::commit();
            $this->info("¡Éxito Total!");
            $this->info("- Dependencias procesadas: $contadorDeps");
            $this->info("- Usuarios titulares creados/actualizados: $contadorUsers");

        } catch (\Exception $e) {
            DB::rollBack();
            $this->error('Error crítico durante la sincronización: ' . $e->getMessage());
        }
    }
}