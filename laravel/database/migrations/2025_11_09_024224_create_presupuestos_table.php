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
        Schema::create('presupuestos', function (Blueprint $table) {
            $table->id('id_presupuesto');


            $table->unsignedBigInteger('id_dependencia');
            $table->foreign('id_dependencia')
                ->references('id_dependencia')
                ->on('dependencias')

                ->cascadeOnDelete();


            $table->integer('anio');
            $table->integer('trimestre');
            $table->decimal('monto_asignado', 18, 2);

            $table->unique(['id_dependencia', 'anio', 'trimestre']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('presupuestos');
    }
};
