<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

// CORRECCIÓN 1: Asegúrate de que diga 'Service' con 'c', no 'Servive'
class NucleoDigitalService
{
    protected $baseUrl;
    protected $token;

    public function __construct()
    {
        $this->baseUrl = env('NUCLEO_API_URL');
        $this->token = env('NUCLEO_API_TOKEN');
    }

    public function obtenerDatos()
    {
        try {
            $response = Http::withToken($this->token)
                ->withoutVerifying() // Ignorar SSL localmente
                ->post($this->baseUrl, [
                    "email" => "toxdzulomar@gmail.com",
                    "password" => "Comedatos@2025"
                ]);

            if ($response->failed()) {
                Log::error('Error API Gobierno: ' . $response->body());
                return null;
            }

            $data = $response->json();
            return $this->formatearDatos($data);

        } catch (\Exception $e) {
            Log::error('Excepción en NucleoDigitalService: ' . $e->getMessage());
            return null;
        }
    }

    private function formatearDatos($externalData)
    {
        // 1. SECTORES (Esto estaba bien)
        $sectores = collect($externalData['datosTablas']['h25_sector'] ?? [])
            ->map(function ($item) {
                return [
                    'id_sector' => $item['id'] ?? null,
                    'nombre_sector' => $item['nombre'] ?? 'Sin nombre',
                    'descripcion' => $item['descripcion'] ?? ''
                ];
            });

        // 2. DEPENDENCIAS (CORRECCIÓN IMPORTANTE)
        // El JSON tiene los datos de contacto en 'comedatos_institucion', 
        // pero es un array dentro de otro array (index 0).
        $listaInstituciones = $externalData['datosTablas']['comedatos_institucion'][0] ?? [];

        $dependencias = collect($listaInstituciones)
            ->map(function ($item) {
                // Usamos el operador '??' para evitar errores si falta algún campo
                $nombre = $item['Nombre_Encargado'] ?? '';
                $apellido = $item['ApellidoPaterno'] ?? '';

                return [
                    // Mapeamos los campos exactos de TU json
                    'nombre_dependencia' => $item['Nombre_Institucion'] ?? 'Sin Nombre',
                    'titular' => trim("$nombre $apellido"),
                    'contacto' => [
                        'email' => $item['Email'] ?? null,
                        'telefono' => $item['Telefono'] ?? null,
                        'direccion' => ($item['Direccion'] ?? '') . ' ' . ($item['Numero'] ?? ''),
                        'redes' => null // Esta tabla no trae redes, lo dejamos null para que no falle
                    ],
                    // Como estamos usando la tabla de directorio, no tenemos misión/visión aquí.
                    // Ponemos defaults para que no rompa el frontend.
                    'institucional' => [
                        'mision' => 'No disponible en esta vista',
                        'vision' => 'No disponible en esta vista',
                        'objetivo' => null
                    ]
                ];
            });

        return [
            'fuente' => 'Núcleo Digital QROO',
            'sectores' => $sectores,
            'dependencias' => $dependencias
        ];
    }
}