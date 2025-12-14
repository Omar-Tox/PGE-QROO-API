<?php

namespace Tests\Feature\Api;

use App\Models\User;
use App\Models\Rol;
use App\Models\Dependencia;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class EdificioTest extends TestCase
{
    use RefreshDatabase;

    public function test_admin_dependencia_puede_crear_edificio_en_su_dependencia()
    {
        // 1. Crear Dependencia y Usuario
        $dependencia = Dependencia::factory()->create();
        $user = User::factory()->create();
        
        // 2. Asignar Rol "Admin Dependencia"
        $rolAdmin = Rol::where('nombre_rol', 'Admin Dependencia')->first();
        $user->roles()->attach($rolAdmin->id_rol, ['dependencia_id' => $dependencia->id_dependencia]);

        // 3. Petición para crear edificio
        $response = $this->actingAs($user)
                         ->postJson("/api/dependencias/{$dependencia->id_dependencia}/edificios", [
                             'nombre_edificio' => 'Torre A',
                             'direccion' => 'Av. Test',
                             'latitud' => 19.0,
                             'longitud' => -88.0
                         ]);

        $response->assertStatus(201);
    }

    public function test_admin_dependencia_NO_puede_crear_edificio_en_OTRA_dependencia()
    {
        // 1. Crear DOS dependencias
        $miDependencia = Dependencia::factory()->create();
        $otraDependencia = Dependencia::factory()->create();
        
        $user = User::factory()->create();
        $rolAdmin = Rol::where('nombre_rol', 'Admin Dependencia')->first();
        
        // 2. Asignar rol SOLO en la primera
        $user->roles()->attach($rolAdmin->id_rol, ['dependencia_id' => $miDependencia->id_dependencia]);

        // 3. Intentar crear en la SEGUNDA
        $response = $this->actingAs($user)
                         ->postJson("/api/dependencias/{$otraDependencia->id_dependencia}/edificios", [
                             'nombre_edificio' => 'Torre Invasora',
                         ]);

        // 4. Esperar prohibición
        $response->assertStatus(403);
    }
}