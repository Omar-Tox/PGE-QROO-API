<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Dependencia;
use App\Models\ConsumoHistorico;
use App\Models\Presupuesto;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;


class DashboardController extends Controller
{
    /**
     * @OA\Get(
     *     path="/api/dashboard",
     *     tags={"Dashboard"},
     *     summary="Datos principales del dashboard",
     *     description="Obtiene KPIs, evolución de consumo y ranking de inmuebles. Puede filtrarse por dependencia.",
     *     security={{"sanctum": {}}},
     *
     *     @OA\Parameter(
     *         name="id_dependencia",
     *         in="query",
     *         required=false,
     *         description="ID de la dependencia para filtrar los datos del dashboard",
     *         @OA\Schema(type="integer", example=2)
     *     ),
     *
     *     @OA\Response(
     *         response=200,
     *         description="Datos del dashboard obtenidos correctamente",
     *         @OA\JsonContent(
     *             @OA\Property(
     *                 property="periodo",
     *                 type="object",
     *                 @OA\Property(property="mes", type="integer", example=6),
     *                 @OA\Property(property="año", type="integer", example=2025)
     *             ),
     *
     *             @OA\Property(
     *                 property="kpis",
     *                 type="object",
     *                 @OA\Property(property="consumo_mes_kwh", type="number", format="float", example=15432.75),
     *                 @OA\Property(property="costo_mes", type="number", format="float", example=32145.50),
     *                 @OA\Property(property="presupuesto_trimestre", type="number", format="float", example=500000.00)
     *             ),
     *
     *             @OA\Property(
     *                 property="data_evolucion",
     *                 type="array",
     *                 @OA\Items(ref="#/components/schemas/EvolucionConsumo")
     *             ),
     *
     *             @OA\Property(
     *                 property="data_inmuebles",
     *                 type="array",
     *                 @OA\Items(ref="#/components/schemas/InmuebleTopConsumo")
     *             )
     *         )
     *     ),
     *
     *     @OA\Response(response=401, description="No autenticado")
     * )
     */
    public function index(Request $request)
    {
        $dependenciaId = $request->query('id_dependencia');

        //Definir las fechas de corte
        $fechaActual = Carbon::now();
        $currentMonth = $fechaActual->month;
        $currentYear = $fechaActual->year;
        // $currentMonth = $request->query('mes', $fechaActual->month);
        // $currentYear = $request->query('año', $fechaActual->year);

        //Prepar las consultas
        $queryConsumo = ConsumoHistorico::query();

        /**
         * Filtrar por dependencia específica
         * Nota: ConsumoHistorico se une a Edificio, y Edificio a Dependencia
         */ 
        if($dependenciaId) {
            $queryConsumo->whereHas('edificio', function($q) use ($dependenciaId) {
                $q->where('dependencia_id', $dependenciaId);
            });
        }

        //Consumo del mes
        $consumoMes = (clone $queryConsumo)
                    ->where('mes', $currentMonth)
                    ->where('año', $currentYear)
                    ->sum('consumo_kwh');
        
        //Costo del mes
        $costoMes = (clone $queryConsumo)
                    ->where('mes', $currentMonth)
                    ->where('año', $currentYear)
                    ->sum('costo_total');

        //Calcular el trimestre
        $trimestre = ceil($currentMonth / 3.0);

        //Calcular el monto de la dependencia especifica
        $presupuestoAsignado = 0;
        if($dependenciaId) {
            $presupuestoAsignado = Presupuesto::where('dependencia_id', $dependenciaId)
                                ->where('año', $currentMonth)
                                ->where('trimestre', $trimestre)
                                ->sum('monto_asignado');
        } else {
            //calcularmos el presupuesto para el superadmin
            $presupuestoAsignado = Presupuesto::where('año', $currentYear)
                                ->where('trimestre', $trimestre)
                                ->sum('monto_asignado');
        }

        // --- Grafica de consumo en un año
        $evolucion = (clone $queryConsumo)
                    ->selectRaw('año, mes, SUM(consumo_kwh) as total_consumo, SUM(costo_total) as total_costo')
                    ->groupBy('año', 'mes')
                    ->orderBy('año', 'desc')
                    ->orderBy('mes', 'desc')
                    ->limit(12)
                    ->get()
                    ->reverse() //Imprimir la gráfica de antiguo - nuevo
                    ->values();
                    
        // --- TABLA: INMUEBLES CON MAYOR CONSUMO (Top 5) ---
        $inmuebles = (clone $queryConsumo)
                    ->join('edificio', 'consumo_historico.edificio_id', '=', 'edificio.id_edificio')
                    ->where('mes', $currentMonth)
                    ->where('año', $currentYear)
                    ->selectRaw('edificio.nombre_edificio, SUM(consumo_kwh) as consumo')
                    ->groupBy('edificio.nombre_edificio')
                    ->orderByDesc('consumo')
                    ->limit(5)
                    ->get();

        return response()->json([
            'periodo' => [
                'mes' => $currentMonth,
                'año' => $currentYear
            ],
            'kpis' => [
                'consumo_mes_kwh' => round($consumoMes, 2),
                'costo_mes' => round($consumoMes, 2),
                'presupuesto_trimestre' => (float)$presupuestoAsignado
            ],
            'data_evolucion' => $evolucion,
            'data_inmuebles' => $inmuebles
        ]);
    }
}
