<?php

namespace Tests\Feature\Api;

use App\Models\User;
use App\Models\Rol;
use App\Models\Dependencia;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class DependenciaTest extends TestCase
{
    use RefreshDatabase;

    public function test_super_admin_puede_ver_todas_las_dependencias()
    {
        // 1. Crear usuario Super Admin
        $admin = User::factory()->create();
        $rolSuperAdmin = Rol::where('nombre_rol', 'Super Admin')->first();
        
        // Asignamos el rol a una dependencia ficticia (Global ID 1)
        $depGlobal = Dependencia::factory()->create();
        $admin->roles()->attach($rolSuperAdmin->id_rol, ['dependencia_id' => $depGlobal->id_dependencia]);

        // 2. Crear dependencias extra para ver si las trae todas
        Dependencia::factory()->count(3)->create();

        // 3. Hacer petición
        $response = $this->actingAs($admin)
                         ->getJson('/api/dependencias');

        // 4. Verificar (Debe ver las 3 creadas + la global = 4)
        $response->assertStatus(200)
                 ->assertJsonCount(4);
    }

    public function test_usuario_sin_permisos_no_puede_crear_dependencia()
    {
        // 1. Crear usuario normal
        $user = User::factory()->create();

        // 2. Intentar crear
        $response = $this->actingAs($user)
                         ->postJson('/api/dependencias', [
                             'nombre_dependencia' => 'Secretaría Hacker'
                         ]);

        // 3. Verificar rechazo (403 Forbidden)
        $response->assertStatus(403);
    }

    public function test_creacion_dependencia_exitosa()
    {
        $admin = User::factory()->create();
        $rolSuperAdmin = Rol::where('nombre_rol', 'Super Admin')->first();
        $depGlobal = Dependencia::factory()->create();
        $admin->roles()->attach($rolSuperAdmin->id_rol, ['dependencia_id' => 1]);

        $response = $this->actingAs($admin)
                         ->postJson('/api/dependencias', [
                             'nombre_dependencia' => 'Nueva Secretaría Test'
                         ]);

        $response->assertStatus(201);
        $this->assertDatabaseHas('dependencias', ['nombre_dependencia' => 'Nueva Secretaría Test']);
    }
}