<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Imports\ConsumoImport;
use Illuminate\Http\Request;
use Maatwebsite\Excel\Facades\Excel;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class ConsumoController extends Controller
{

    use AuthorizesRequests;

    public function cargaMasiva(Request $request) {

        $this->authorize('cargar-consumos');

        $request->validate([
            'archivo' => 'required|file|mimes:csv,xlsx,xls,txt'
        ]);

        try {
            //Ejecutar la carga mediante el import
            Excel::import(new ConsumoImport, $request->file('archivo'));

            return response()->json([
                'message' => 'Datos importados con exito'
            ], 201);

        } catch (\Maatwebsite\Excel\Validators\ValidationException $e) {
            // Capturar errores de validación DENTRO del Excel (fila por fila)
            $fallas = $e->failures();

            $errores = [];

            foreach($fallas as $falla) {
                $errores[] = [
                    'fila' => $falla->row(),
                    'columna' => $falla->attribute(),
                    'error' => $falla->errors(),
                    'valor_erroneo' => $falla->values()[$falla->attribute()]
                ];
            }

            return response()->json([
                'message' => 'El archivo tiene errores de formato',
                'details' => $errores
            ], 422);

        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Error al leer el archivo',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
