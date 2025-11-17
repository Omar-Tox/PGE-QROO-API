<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Presupuesto extends Model
{
    //
    use HasFactory;

    protected $table = 'presupuestos';
    protected $primaryKey = 'id_presupuesto';
    public $timestamps = false;
    protected $fillable = [
        'dependencia_id',
        'año',
        'trimestre',
        'monto_asignado'
    ];

    public function dependencia () {
        return $this->belongsTo(Dependencia::class, 'dependencia_id', 'id_dependencia');
    }
}
