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
            $table->foreignId('usuario_id')
                ->constrained('usuarios', 'id_usuario')
                ->cascadeOnDelete();

            $table->foreignId('dependencia_id')
                ->constrained('dependencias', 'id_dependencia')
                ->cascadeOnDelete();

            $table->foreignId('rol_id')
                ->constrained('roles', 'id_rol')
                ->cascadeOnDelete();
                
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
