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
        Schema::create('consumo_tiempo_real', function (Blueprint $table) {
            $table->id('id_registro');
            $table->foreignId('edificio_id')->constrained('edificios')->cascadeOnDelete();
            $table->string('id_sensor', 100);
            $table->timestamp('timestamp_registro')->useCurrent();
            $table->decimal('consumo_energetico', 18, 4);
            $table->decimal('potencia', 18, 4);
            $table->decimal('energia', 18, 4);

        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('consumo_tiempo_real');
    }
};
