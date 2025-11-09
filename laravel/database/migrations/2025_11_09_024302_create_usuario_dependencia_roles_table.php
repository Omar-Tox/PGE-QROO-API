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
            $table->foreingId('usuario_id')->constrained('usuarios')->cascadeOnDelete();
            $table->foreingId('dependencia_id')->constrained('dependencias')->cascadeOnDelete();
            $table->foreingId('rol_id')->constrained('roles')->cascadeOnDelete();
            
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
