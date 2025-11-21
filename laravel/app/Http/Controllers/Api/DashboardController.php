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
     * Obtiene los KPIs y datos para el Dashboard principal.
     * Puede filtrar por dependencia_id si se pasa en el query param.
     * Ejemplo: /api/dashboard?dependencia_id=2
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

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
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
