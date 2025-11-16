<?php

namespace App\Providers;

use Illuminate\App\Models\User;
use Illuminate\App\Models\Dependencia;
use Illuminate\Support\Facades\Gate;
use Illuminate\Foundation\Support\Providers\AuthServiceProvider as ServiceProvider;


class AuthServiceProvider extends ServiceProvider
{
    /**
     * Register services.
     */
    public function register(): void
    {
        //
    }

    /**
     * The model to policy mappings for the application.
     *
     * @var array<class-string, class-string>
     */
    protected $policies = [
        //
    ];


    /**
     * Bootstrap services.
     */
    public function boot(): void
    {

        // =============================================================
        // GLOBAL GATES
        // =============================================================

        Gate::define('crear_dependencia', function(User $user) {
            return $user->hasGlobalPermisson('crear_dependencias');
        });

        Gate::define('ver-lista-usuarios', function(User $user) {
            return $user->hasGlobalPermisson('ver_usuarios_global');
        });

        Gate::define('ver-dependencia', function(User $user, Dependencia $dependencia) {
            return $user->dependencias()
                        ->where('dependencias.id_dependencia', $dependencia->id_dependencia)
                        ->exists();
        });

        Gate::define('actualizar-dependencia', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissonFor('editar_dependencias', $dependencia);
        });

        Gate::define('eliminar_dependencia', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissonFor('eliminar_dependencias', $dependencia);
        });

        Gate::define('ver_presupuestos', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissonFor('ver_presupuestos', $dependencia);
        });

        Gate::define('asignar-presupuesto', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissonFor('asignar_presupuestos', $dependencia);
        });

        /**
         * Nota:
         * Falta por agregar: 'ver_edificios', 'crear_edificio', 'cargar_consumos', etc.)
         */        
    }
}
