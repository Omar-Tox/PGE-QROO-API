<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Dependencia extends Model
{
    protected $table = 'dependencias';
    protected $primaryKey = 'id_dependencia';
    public $timestamps = false;

    protected $fillable = [
        'nombre_dependencia', 
        'sector_id'
    ];

    public function sector () {
        return $this->belongsTo(Sector::class, 'sector_id', 'id_sector');
    }

    public function edificios () {
        return $this->hasMany(Edificio::class, 'id_dependencia', 'dependencia_id');
    }

    public function presupuestos () {
        return $this->hasMany(Presupuesto::class, 'id_dependencia', 'dependencia_id');
    }

    public function usuarios () {
        return $this->belongsToMany(User::class, 'usuario_dependencia_roles', 'dependencia_id', 'usuario_id')
                    ->withPivot('rol_id');
    }
}
