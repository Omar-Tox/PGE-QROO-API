<?php

namespace Database\Seeders;


use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $this->call([
            PermisosSeeder::class,
            SectoresSeeder::class,
            DependenciasSeeder::class,
            EdificiosSeeder::class,
            RolesSeeder::class,
            UsuariosSeeder::class,
            PresupuestosSeeder::class,
            ConsumoHistoricoSeeder::class,
        ]);
    }
}
