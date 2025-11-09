<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('usuarios', function (Blueprint $table) {
            $table->id('id_usuario');
            $table->string('nombre_usuario', 150)->unique();
            $table->string('nombre', 50);
            $table->string('apellido', 50);
            $table->string('email', 255)->unique();
            $table->string('contresena', 128);
            $table->boolean('activo')->default(true);
             $table->timestamp('fecha_registro')->useCurrent();
             $table->timestamp('ultimo_login')->nullable();

        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('usuarios');
    }
};
