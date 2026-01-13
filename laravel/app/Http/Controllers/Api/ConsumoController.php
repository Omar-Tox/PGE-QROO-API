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
    /**
 * @OA\Post(
 *     path="/api/consumos/carga-masiva",
 *     tags={"Consumos"},
 *     summary="Carga masiva de consumos energéticos",
 *     description="Permite importar consumos desde un archivo CSV, XLSX, XLS o TXT. Requiere permiso cargar-consumos.",
 *     security={{"sanctum": {}}},
 *
 *     @OA\RequestBody(
 *         required=true,
 *         @OA\MediaType(
 *             mediaType="multipart/form-data",
 *             @OA\Schema(
 *                 required={"archivo"},
 *                 @OA\Property(
 *                     property="archivo",
 *                     type="string",
 *                     format="binary",
 *                     description="Archivo de consumos (csv, xlsx, xls, txt)"
 *                 )
 *             )
 *         )
 *     ),
 *
 *     @OA\Response(
 *         response=201,
 *         description="Datos importados con éxito",
 *         @OA\JsonContent(
 *             @OA\Property(property="message", type="string", example="Datos importados con exito")
 *         )
 *     ),
 *
 *     @OA\Response(
 *         response=422,
 *         description="Errores de validación en el archivo",
 *         @OA\JsonContent(
 *             @OA\Property(property="message", type="string", example="El archivo tiene errores de formato"),
 *             @OA\Property(
 *                 property="details",
 *                 type="array",
 *                 @OA\Items(ref="#/components/schemas/ErrorCargaConsumo")
 *             )
 *         )
 *     ),
 *
 *     @OA\Response(response=403, description="No autorizado"),
 *     @OA\Response(response=500, description="Error interno al procesar el archivo")
 * )
 */
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
