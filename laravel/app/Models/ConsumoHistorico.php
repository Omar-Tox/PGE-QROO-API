<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class ConsumoHistorico extends Model
{
    // uses
    use HasFactory;

    protected $table = 'consumo_historico';
    protected $primaryKey = 'id_consumo_historico';
    public $timestamp = 'fecha_registro';

    protected $fillable = [
        'edificio_id',
        'año',
        'mes',
        'consumo_kwh',
        'costo_total',
        'fuente_dato'
    ];

    public function edificios () {
        return $this->belongsTo(Edificio::class, 'edificio_id', 'id_edificio');
    }
}
