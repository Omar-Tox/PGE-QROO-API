<?php

namespace Tests;

use Illuminate\Foundation\Testing\TestCase as BaseTestCase;
use Database\Seeders\PermisosSeeder;
use Database\Seeders\RolesSeeder;
use Database\Seeders\SectoresSeeder;

abstract class TestCase extends BaseTestCase
{
    //función para ejecutar cada prueba individual
    protected function setUp(): void {
        parent::setUp();

        $this->seed(PermisosSeeder::class);
        $this->seed(RolesSeeder::class);
        $this->seed(SectoresSeeder::class);
    }
}
