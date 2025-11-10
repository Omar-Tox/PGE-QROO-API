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
        Schema::create('rol_permisos', function (Blueprint $table) {
            // 🔹 Relación con 'roles'
            $table->unsignedBigInteger('id_rol');
            $table->foreign('id_rol')
                ->references('id_rol')
                ->on('roles')
                ->cascadeOnDelete();

            // 🔹 Relación con 'permisos'
            $table->unsignedBigInteger('id_permiso');
            $table->foreign('id_permiso')
                ->references('id_permiso')
                ->on('permisos')
                ->cascadeOnDelete();

            // 🔹 Clave primaria compuesta
            $table->primary(['id_rol', 'id_permiso']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('rol_permisos');
    }
};
