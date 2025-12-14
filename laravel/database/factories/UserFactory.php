<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\User>
 */
class UserFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            // Usamos TUS columnas personalizadas
            'nombre_usuario' => $this->faker->unique()->userName(),
            'nombre' => $this->faker->firstName(),
            'apellido' => $this->faker->lastName(),
            'email' => $this->faker->unique()->safeEmail(),
            
            // El mutator en tu modelo User se encargará de hashear esto
            'contrasena' => 'password', 
            
            'activo' => true,
            'fecha_registro' => now(),
            
            // 'ultimo_login' lo dejamos null por defecto
        ];
    }

    /**
     * Indicate that the model's email address should be unverified.
     */
    public function unverified(): static
    {
        return $this->state(fn (array $attributes) => [
            // Tu tabla no tiene email_verified_at, así que comentamos o quitamos esto
            // 'email_verified_at' => null,
        ]);
    }
}