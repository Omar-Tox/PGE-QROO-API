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
        Schema::create('dependencias', function (Blueprint $table) {
            $table->id('id_dependencia');
            $table->string('nombre_dependencia', 255)->unique();
            $table->foreignId('sector_id')
                ->nulleable()
                ->constrained('sector')
                ->nullOnDelete(); // Permite que si sector se elimina, este valor sea NULL
            
            $table->timestamp('fecha_alta')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('dependencias');
    }
};
