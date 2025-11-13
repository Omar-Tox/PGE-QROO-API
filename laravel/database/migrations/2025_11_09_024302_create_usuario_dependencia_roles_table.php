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
        Schema::create('usuario_dependencia_roles', function (Blueprint $table) {

            $table->unsignedBigInteger('usuario_id')->foreignId('usuario_id')->references('usuario_id')->on('usuarios')->cascadeOnDelete();
            $table->unsignedBigInteger('dependencia_id')->foreignId('dependencia_id')->references('dependencia_id')->on('dependencias')->cascadeOnDelete();
            $table->unsignedBigInteger('rol_id')->foreignId('rol_id')->references('rol_id')->on('roles')->cascadeOnDelete();

            $table->primary(['usuario_id', 'dependencia_id', 'rol_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('usuario_dependencia_roles');
    }
};
