<?php

namespace Database\Factories;

use App\Models\Edificio;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\ConsumoHistorico>
 */
class ConsumoHistoricoFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'edificio_id' => Edificio::factory(),
            'año' => $this->faker->numberBetween(2020, 2025),
            'mes' => $this->faker->numberBetween(1, 12),
            'consumo_kwh' => $this->faker->randomFloat(2, 100, 10000),
            'costo_total' => $this->faker->randomFloat(2, 20000, 200000),
            'fuente_dato' => 'Simulado',
            'fecha_registro' => now()
        ];
    }
}
