<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void 
    {
        Schema::create('consumo_historico', function (Blueprint $table) {
            $table->id();
            $table->foreignId('edificio_id')
                ->constrained('edificio')
                ->cascadeOnDelete();

            $table->integer('anio');
            $table->integer('mes');
            $table->decimal('consumo_kwh', 18, 2);
            $table->decimal('costo_total', 18, 2);
            $table->string('fuente_dato', 100)->nullable();
            $table->timestamp('fecha_registro')->useCurrent();

            $table->unique(['edificio_id', 'anio', 'mes']);
        });
    }
    
    /**
     * Reverse the migrations.
     */
    public function down(): void 
    {
        Schema::dropIfExists('consumo_historico');
    }
};
