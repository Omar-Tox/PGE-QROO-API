<?php

namespace App\Providers;

use App\Models\User;
use App\Models\Dependencia;
use App\Models\Edificio;
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
        
        // === Gates globales ===

        Gate::define('crear-dependencia', function(User $user) {
            return $user->hasGlobalPermission('crear_dependencias');
        });

        Gate::define('ver-lista-usuarios', function(User $user) {
            return $user->hasGlobalPermission('ver_usuarios_global');
        });

        // gate::define('crear-usuario'), function(User $user) {
        //     return $user->hasGlobalPermission('crear_usuario');
        // }

        // === Gates específicos para las dependencias ===

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


        /**
         * Gates para presupuestos
         */

        Gate::define('ver-presupuestos', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissionFor('ver_presupuestos', $dependencia);
        });

        Gate::define('asignar-presupuesto', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissionFor('asignar_presupuestos', $dependencia);
        });
        
        /**
         * Gates para edificios
         */

        Gate::define('ver-edificios', function(User $user, Dependencia $dependencia){
            return $user->hasPermissionFor('ver_edificios', $dependencia);
        });

        Gate::define('crear-edificio', function(User $user, Dependencia $dependencia) {
            return $user->hasPermissionFor('crear_edificios', $dependencia);
        });

        // Gate de cargar consumo
        
        Gate::define('cargar-consumos', function(User $user){
            if($user->hasGlobalPermission('cargar_consumos')) {
                return true;
            }

            /**
             * Verificar si tiene el permiso en alguna de sus dependencias asignadas
             * Recorremos todas las dependencias del usuario
             */
            foreach($user->dependencias as $dependencia) {
                if($user->hasPermissionFor('cargar_consumos', $dependencia)) {
                    return true;
                }
            }

            return false;
        });
    }
}
