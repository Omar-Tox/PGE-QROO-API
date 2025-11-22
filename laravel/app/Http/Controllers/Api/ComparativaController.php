<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\ConsumoHistorico;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class ComparativaController extends Controller
{
    /**
     * Obtiene el ranking de consumo por dependencia.
     * Útil para la gráfica de barras "Comparativa de Consumo".
     */
    public function index(Request $request)
    {
        //filtros
        $currentData = Carbon::now();
        $año = $request->query('año', $currentData->year);
        $mes = $request->query('mes');

        // Consulta de consumo Histórico
        $query = ConsumoHistorico::query()
                            ->join('edificio', 'consumo_historico.edificio_id', '=', 'edificio.id_edificio')
                            ->join('dependencias', 'edificio.dependencia_id', '=', 'dependencias.id_dependencia');

        //Filtros de tiempo
        $query->where('consumo_historico.año', $año);
        if($mes) {
            $query->where('consumo_historico.mes', $mes);
        }

        //agrupar los datos
        $ranking = $query->select(
            'dependencias.id_dependencia',
            'dependencias.nombre_dependencia',
            DB::raw('SUM(consumo_historico.consumo_kwh) as total_consumo'),
            DB::raw('SUM(consumo_historico.costo_total) as total_costo')
        )
        ->groupBy('dependencias.id_dependencia', 'dependencias.nombre_dependencia')
        ->orderByDesc('total_consumo')
        ->get();

        return response()->json([
            'periodo' => [
                'año' => $año,
                'mes' => $mes ?? 'Todos'
            ],
            'ranking' => $ranking
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
