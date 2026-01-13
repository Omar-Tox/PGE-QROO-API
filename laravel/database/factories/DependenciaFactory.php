<?php

namespace Database\Factories;
use App\Models\Sector;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Dependencia>
 */
class DependenciaFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'nombre_dependencia' => $this->faker->unique()->company(),
            'sector_id' => Sector::factory(),
            'fecha_alta' => now()
        ];
    }
}
