<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Permiso extends Model
{
    use HasFactory;
    protected $table = 'permisos';
    protected $primaryKey = 'id_permiso';
    public $timestamps = false;

    protected  $filled = [
        'nombre_permiso',
        'descripcion'
    ];

    public function roles () {
        return $this->belongsToMany(Rol::class, 'rol_pemisos', 'permiso_id', 'rol_id');
    }
}
