<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Dependencia;
use App\Models\Presupuesto;
use Illuminate\Support\Facades\Gate;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class PresupuestoController extends Controller
{
    use AuthorizesRequests;
    /**
     * Muestra los presupuestos de una dependencia específica.
     */

    public function index(Dependencia $dependencia)
    {
        // Autorizar si el usuario puede 'ver-presupuesto' de ESTA dependencia
        $this->authorize('ver-presupuestos', $dependencia);

        // Devolver los presupuestos de la dependencia por años
        return response()->json(
            $dependencia->presupuestos()
                        ->orderBy('año', 'desc')
                        ->orderBy('trimestre', 'desc')
                        ->get()
        );
    }

    /**
     * Asigna un nuevo presupuesto a una dependencia.
     */
    public function store(Request $request, Dependencia $dependencia)
    {
        $this->authorize('asignar-presupuesto', $dependencia);

        $validatedData = $request->validate([
            'año' => 'required|integer|min:2020|max:2050',
            'trimestre' => 'required|integer|min:1|max:4',
            'monto_asignado' => 'required|numeric|min:0'
        ]);

        /**
         * Validar que los datos no esten duplicados
         */
        $exists = $dependencia->presupuestos()
                            ->where('año', $validatedData['año'])
                            ->where('trimestre', $validatedData['trimestre'])
                            ->exists();

        if($exists) {
            return response()->json(
                ['message' => 'Ya existe un presupuesto para este año o trimestre', 409]
            );
        }

        $presupuesto = $dependencia->presupuestos()->create($validatedData);
        
        return response()->json($presupuesto, 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
