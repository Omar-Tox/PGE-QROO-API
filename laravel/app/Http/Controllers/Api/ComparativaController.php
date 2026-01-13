<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\ConsumoHistorico;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class ComparativaController extends Controller
{/**
     * @OA\Get(
     *     path="/api/analisis/ranking-dependencias",
     *     tags={"Análisis"},
     *     summary="Ranking de consumo por dependencia",
     *     description="Obtiene el ranking de consumo energético agrupado por dependencia. Útil para gráficas comparativas. Permite filtrar por año y mes.",
     *     security={{"sanctum": {}}},
     *
     *     @OA\Parameter(
     *         name="año",
     *         in="query",
     *         required=false,
     *         description="Año del consumo (por defecto el año actual)",
     *         @OA\Schema(type="integer", example=2025)
     *     ),
     *
     *     @OA\Parameter(
     *         name="mes",
     *         in="query",
     *         required=false,
     *         description="Mes del consumo (1–12). Si no se envía, se consideran todos los meses",
     *         @OA\Schema(type="integer", minimum=1, maximum=12, example=3)
     *     ),
     *
     *     @OA\Response(
     *         response=200,
     *         description="Ranking de consumo obtenido correctamente",
     *         @OA\JsonContent(
     *             @OA\Property(
     *                 property="periodo",
     *                 type="object",
     *                 @OA\Property(property="año", type="integer", example=2025),
     *                 @OA\Property(property="mes", type="string", example="Todos")
     *             ),
     *             @OA\Property(
     *                 property="ranking",
     *                 type="array",
     *                 @OA\Items(ref="#/components/schemas/RankingConsumoDependencia")
     *             )
     *         )
     *     ),
     *
     *     @OA\Response(
     *         response=401,
     *         description="No autenticado"
     *     )
     * )
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
}
