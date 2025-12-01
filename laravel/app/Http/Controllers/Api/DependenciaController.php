<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Dependencia;
use App\Models\Edificio;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class DependenciaController extends Controller
{
    use AuthorizesRequests;
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $user = $request->user();

        if($user->hasGlobalPermission('crear_dependencias')) {
            $dependencias = Dependencia::with('sector')
                                        ->withCount('edificios')
                                        ->get();

        }
        else {
            $dependencias = $user->dependencias()
                        ->with('edificios', 'sector')
                        ->withCount('edificios')
                        ->get();

        }
        return response()->json($dependencias);
    }

    /**
     * Store a newly created dependence in storage.
     */
    public function store(Request $request)
    {
        //Autorizamos la acción
        $this->authorize('crear-dependencia');

        $validatedData =$request->validate([
            'nombre_dependencia' => 'required|string|max:255|unique:dependencias',
            'sector_id' => 'nullable|integer|exists:sector,id_sector',
        ]);

        $dependencia = Dependencia::create($validatedData);

        return response()->json($dependencia, 201);
    }

    /**
     * Display the specified dependence.
     */
    public function show(Dependencia $dependencia)
    {
        // Autorizamos usando el Gate 'ver-dependencia'.
        // Laravel pasa automáticamente el usuario autenticado y la $dependencia
        $this->authorize('ver-dependencia', $dependencia);

        // Si pasa la autorización, mostrarlas
        $dependencia->load('edificios', 'presupuestos', 'sector')
                    ->loadCount('edificios');

        return response()->json($dependencia);
    }

    /**
     * Update the specified dependence in storage.
     */
    public function update(Request $request, Dependencia $dependencia)
    {
        // Autorizar la acción de actualizar
        $this->authorize('actualizar-dependencia', $dependencia);

        $validatedData = $request->validate([
            'nombre_dependencia' => 'sometimes|required|string|max:255|unique:dependencias,nombre_dependencia,' . $dependencia->id_dependencia . ',id_dependencia',
            'sector_id' => 'sometimes|integer|exists:sector,id_sector'
        ]);

        $dependencia->update($validatedData);

        return response()->json($dependencia);
    }

    /**
     * Remove the specified dependence from storage.
     */
    public function destroy(Dependencia $dependencia)
    {
        // Autorizar la acción de eliminar
        $this->authorize('eliminar-dependencia', $dependencia);

        $dependencia->delete();

        return response()->json(
            ['message' => 'Dependencia eliminada con exito']
        );

    }
}
