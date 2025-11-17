<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;


class Rol extends Model
{
    use HasFactory;
    
    protected $table = 'roles';
    protected $primaryKey = 'id_rol';
    public $timestamps = false;

    protected $filled = [
        'nombre_rol',
        'descripcion'
    ];

    public function permisos () {
        return $this->belongsToMany(Permiso::class, 'rol_permisos', 'rol_id', 'permiso_id');
    }

    public function usuarios () {
        return $this->belongsToMany(User::class, 'usuario_dependencia_roles', 'rol_id', 'usuario_id')
                    ->withPivot('dependencia_id');
    }
}
