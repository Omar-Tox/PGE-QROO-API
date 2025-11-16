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
        'contrasena',
        'activo',
    ];

    /**
     * The attributes that should be hidden for serialization.
     *
     * @var list<string>
     */
    protected $hidden = [
        'contrasena'
    ];

    public function getAuthPassword() {
        return $this->contrasena;
    }

    public function contrasena(): Attribute {
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

    public function dependencias() {
        return $this->belongsToMany(Dependencia::class, 'usuario_dependencia_roles', 'usuario_id', 'dependencia_id')
                    ->withPivot('rol_id')->distinct();
    }

    // --- MÉTODOS DE AUTORIZACIÓN ---
    /**
     * Verifica si el usuario tiene un permiso específico para su dependencia dada.
     * 
     * @param string $permissionName El nombre del permiso (ej. 'editar_presupuestos')
     * @param \App\Models\Dependencia $dependencia El contexto de la dependencia
     * @return bool
     */

    public function hasPermissionFor(String $permissionName, App\Models\Dependencia $dependencia):bool {
        $roles = $this->roles()
                    ->wherePivot('dependencia_id', $dependencia->id_dependencia)
                    ->with('permisos')
                    ->get();
        
        //Verificar si el usuario no tiene roles asignados para esta dependencia
        if($roles->isEmpty()) {
            return false;
        }

        //Recorrer los roles y sus permisos para ver si alguno coincide
        foreach($roles as $rol) {
            if($rol->permisos->contains('nombre_permiso', $permissionName)) {
                return true;
            }
        }

        return false;
    }

    /**
     * Verifica si el usuario tiene un permiso "Global".
     * Asumimos que "Global" es una dependencia especial con ID = 1.
     *
     * @param string $permissionName El nombre del permiso (ej. 'crear_dependencias')
     * @return bool
     */

    public function hasGlobalPermission(String $permissionName): bool {

        $globalDependenciaId = 1;

        $roles = $this->roles()
                    ->wherePivot('dependencia_id', $globalDependenciaId)
                    ->with('permisos')
                    ->get();

        if($roles->isEmpty()) {
            return false;
        }

        foreach($roles as $rol) {
            if($rol->permisos->contains('nombre_perniso', $permissionName)) return true;
        }

        return false;
    }
}
