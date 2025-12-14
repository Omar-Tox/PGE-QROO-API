<?php

namespace Database\Factories;
use App\Models\Dependencia;

use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Presupuesto>
 */
class PresupuestoFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'dependencia_id' => Dependencia::factory(),
            'año' => $this->faker->numberBetween(2020, 2025),
            'trimestre' => $this->faker->numberBetween(1, 4),
            'monto_asignado' => $this->faker->randomFloat(2, 50000, 5000000)
        ];
    }
}
