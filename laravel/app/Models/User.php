<?php

namespace App\Models;

// use Illuminate\Contracts\Auth\MustVerifyEmail;
// use Illuminate\Database\Eloquent\Factories\HasFactory;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;
use Illuminate\Database\Eloquent\Casts\Attribute;
use Illuminate\Support\Facades\Hash;

class User extends Authenticatable
{
    /** @use HasFactory<\Database\Factories\UserFactory> */
    use HasApiTokens, Notifiable;

    protected $table = 'usuarios';
    protected $primaryKey = 'id_usuario';
    public $timestamps = false;

    /**
     * The attributes that are mass assignable.
     *
     * @var list<string>
     */
    protected $fillable = [
        'nombre_usuario',
        'nombre',
        'apellido',
        'email',
        'contresena',
        'activo',
    ];

    /**
     * The attributes that should be hidden for serialization.
     *
     * @var list<string>
     */
    protected $hidden = [
        'contresena'
    ];

    public function getAuthPassword() {
        return $this->contrasena;
    }

    public function password (): Attribute {
        return Attribute::make(
            set: fn ($value) => Hash::make($value),
        );
    }

    /**
     * Relacion pivote compleja
     * Un usuario puede tener muchos roles en muchas dependencias
     */
    public function roles() {
        return $this->belongsToMany(Rol::class, 'usuario_dependencia_roles', 'usuario_id', 'rol_id')
                    ->withPivot('dependencia_id');
    }

    public function dependencias () {
        return $this->belongsToMany(Dependencia::class, 'usuario_dependencia_roles', 'usuario_id', 'dependencia_id')
                    ->withPivot('rol_id')->distinct();
    }
}
