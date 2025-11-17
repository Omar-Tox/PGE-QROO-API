<?php

namespace App\Providers;

use App\Models\User;
use App\Models\Dependencia;
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
        $this->registerPolicies();
        // =============================================================
        // GLOBAL GATES
        // =============================================================

        Gate::define('crear-dependencia', function(User $user) {
            return $user->hasGlobalPermission('crear_dependencias');
        });

        Gate::define('ver-lista-usuarios', function(User $user) {
            return $user->hasGlobalPermission('ver_usuarios_global');
        });

        Gate::define('ver-dependencia', function(User $user, Dependencia $dependencia) {
            return $user->dependencias()
                        ->where('dependencias.id_dependencia', $dependencia->id_dependencia)
                        ->exists();
        });

        Gate::define('actualizar-dependencia', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissionFor('editar_dependencias', $dependencia);
        });

        Gate::define('eliminar-dependencia', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissionFor('eliminar_dependencias', $dependencia);
        });

        Gate::define('ver-presupuestos', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissionFor('ver_presupuestos', $dependencia);
        });

        Gate::define('asignar-presupuesto', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissionFor('asignar_presupuestos', $dependencia);
        });

        /**
         * Nota:
         * Falta por agregar: 'ver_edificios', 'crear_edificio', 'cargar_consumos', etc.)
         */        
    }
}
