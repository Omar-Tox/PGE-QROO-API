<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class EdificiosSeeder extends Seeder
{
    public function run(): void
    {
        DB::statement('TRUNCATE TABLE edificio RESTART IDENTITY CASCADE');

        DB::table('edificio')->insert([
            ['dependencia_id' => 2, 'nombre_edificio' => 'Edificio Central SEQ', 'direccion' => 'Av. Insurgentes 123', 'latitud' => 18.500000, 'longitud' => -88.300000, 'caracteristicas' => 'Oficinas administrativas'],
            ['dependencia_id' => 3, 'nombre_edificio' => 'Campus Chetumal UQROO', 'direccion' => 'Blvd. Bahía s/n', 'latitud' => 18.505000, 'longitud' => -88.285000, 'caracteristicas' => 'Campus principal'],
            ['dependencia_id' => 4, 'nombre_edificio' => 'Hospital General de Chetumal', 'direccion' => 'Av. Independencia 456', 'latitud' => 18.510000, 'longitud' => -88.290000, 'caracteristicas' => 'Hospital regional'],
            ['dependencia_id' => 5, 'nombre_edificio' => 'Planta de Tratamiento CAPA', 'direccion' => 'Carretera Calderitas km 5', 'latitud' => 18.520000, 'longitud' => -88.270000, 'caracteristicas' => 'Planta de tratamiento'],
            ['dependencia_id' => 6, 'nombre_edificio' => 'Centro de Operaciones SEOP', 'direccion' => 'Av. Universidad 789', 'latitud' => 18.508000, 'longitud' => -88.295000, 'caracteristicas' => 'Base de maquinaria'],
            ['dependencia_id' => 7, 'nombre_edificio' => 'Oficinas Centrales SEFIPLAN', 'direccion' => 'Blvd. Bahía 230', 'latitud' => 18.497000, 'longitud' => -88.302000, 'caracteristicas' => 'Centro financiero'],
            ['dependencia_id' => 8, 'nombre_edificio' => 'COBAQROO Plantel 1', 'direccion' => 'Av. Maxuxac 410', 'latitud' => 18.511000, 'longitud' => -88.298000, 'caracteristicas' => 'Educación media superior'],
            ['dependencia_id' => 9, 'nombre_edificio' => 'Edificio Ambiental SEMA', 'direccion' => 'Col. Centro', 'latitud' => 18.503000, 'longitud' => -88.294000, 'caracteristicas' => 'Oficinas ambientales'],
            ['dependencia_id' => 10, 'nombre_edificio' => 'Oficinas IFEQROO', 'direccion' => 'Av. Álvaro Obregón 612', 'latitud' => 18.507000, 'longitud' => -88.291000, 'caracteristicas' => 'Infraestructura escolar'],
            ['dependencia_id' => 11, 'nombre_edificio' => 'Centro de Salud Mental SESA', 'direccion' => 'Av. Erick Paolo Martínez', 'latitud' => 18.512000, 'longitud' => -88.287000, 'caracteristicas' => 'Unidad especializada'],
        ]);
    }
}