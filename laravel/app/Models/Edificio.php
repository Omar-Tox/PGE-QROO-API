<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Edificio extends Model
{
    use HasFactory;

    protected $table = 'edificio';
    protected $primaryKey = 'id_edificio';
    public $timestamp = false;

    protected $fillable = [
        'dependencia_id',
        'nombre_edificio',
        'direccion',
        'latitud',
        'longitud',
        'caracteristicas'
    ];

    public function dependencia () {
        return $this->belongsTo(Dependencia::class, 'dependencia_id', 'id_dependencia');
    }

    public function consumoHistorico () {
        return $this->hasMany(ConsumoHistorico::class, 'edificio_id', 'id_edificio');
    }

    public function consumoTiempoReal () {
        return $this-hasMany(ConsumoTiempoReal::class, 'edificio_id', 'id_edificio');
    }
}
