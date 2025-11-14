<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class ConsumoTiempoReal extends Model
{
    use HasFactory;
    protected $table = 'consumo_tiempo_real';
    protected $primaryKey = 'id_registro';
    public $timestamps = false;

    protected $filled = [
        'edificio_id',
        'id_sensor',
        'timestamp_registro',
        'consumo_energetico',
        'potencia',
        'energia'
    ];

    public function edificio() {
        return $this->belongsTo(Edificio::class, 'edificio_id', 'id_edificio');
    }
}
