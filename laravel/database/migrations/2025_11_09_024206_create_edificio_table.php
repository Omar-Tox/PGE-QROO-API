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
        Schema::create('edificio', function (Blueprint $table) {

            $table->id('id_edificio'); // 🔹 Clave primaria

            $table->unsignedBigInteger('id_dependencia');
            $table->foreign('id_dependencia')
                ->references('id_dependencia')
                ->on('dependencias')

                ->cascadeOnDelete();

            $table->string('nombre_edificio', 255);
            $table->string('direccion', 500)->nullable();
            $table->decimal('latitud', 9, 6)->nullable();
            $table->decimal('longitud', 9, 6)->nullable();
            $table->string('caracteristicas', 500)->nullable();
            $table->timestamp('fecha_alta')->useCurrent(); // 🔹 Por consistencia con tus demás tablas
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('edificio');
    }
};
