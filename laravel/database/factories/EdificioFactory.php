<?php

namespace Database\Factories;
use App\Models\Dependencia;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Edificio>
 */
class EdificioFactory extends Factory
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
            'nombre_edificio' => $this->faker->streetName(),
            'direccion' => $this->faker->address(),
            'latitud' => $this->faker->latitude(18.0, 21.5),
            'longitud' => $this->faker->longitude(-89.5, -86.5),
            'caracteristicas' => $this->faker->text(100)
        ];
    }
}
