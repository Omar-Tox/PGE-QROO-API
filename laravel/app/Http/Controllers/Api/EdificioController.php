<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Dependencia;
use App\Models\Edificio;
use Illuminate\Support\Facades\Gate;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class EdificioController extends Controller
{

    use AuthorizesRequests;
    /**
     * Display a listing of the resource.
     */
    public function index(Dependencia $dependencia)
    {
        // Autorizar si el usuario puede 'ver-edificios' de ESTA dependencia
        $this->authorize('ver-edificios', $dependencia);

        // Devolver los edificios de esa dependencia
        return response()->json($dependencia->edificios);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request, Dependencia $dependencia)
    {
        /**
         * Autorizar si el usuario puede crear un nuevo edificio
         * para su dependencia
         */ 

        $this->authorize('crear-edificio', $dependencia);

        $validatedData = $request->validate([
            'nombre_edificio' => 'required|string|max:255',
            'direccion' => 'nullable|string|max:500',
            'latitud' => 'nullable|numeric|between:-90,90',
            'longitud' => 'nullable|numeric|between:-180,180',
            'caracteristicas' => 'nullable|string|max:500',
        ]);

        $edificio = $dependencia->edificios()->create($validatedData);

        return response()->json($edificio, 201);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Edificio $edificio)
    {
        $this->authorize('actualizar-edificio', $edificio);

        $validatedData = $request->validate([
            'nombre_edificio' => 'sometimes|required|string|max:255',
            'direccion' => 'nullable|string|max:500',
            'latitud' => 'nullable|numeric|between:-90,90',
            'longitud' => 'nullable|numeric|between:-180,180',
            'caracteristicas' => 'nullable|string',
        ]);

        $edificio->update($validatedData);
        return response()->json($edificio);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Edificio $edificio)
    {
        $this->authorize('eliminar-edificio', $edificio);
        $edificio->delete();
        return response()->json([
            'message' => 'Edificio eliminado'
        ]);

    }
}
