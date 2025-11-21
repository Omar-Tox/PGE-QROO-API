<?php

namespace App\Imports;

use App\Models\ConsumoHistorico;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithValidation;


class ConsumoImport implements ToModel, WithHeadingRow, WithValidation
{
    /**
    * @param array $row
    *
    * @return \Illuminate\Database\Eloquent\Model|null
    */
    public function model(array $row)
    {

        // Laravel Excel convierte las cabeceras a 'snake_case'.
        // Ejemplo: "Consumo kWh" en el Excel se lee como $row['consumo_kwh']
        return new ConsumoHistorico([
            'edificio_id' => $row['id_edificio'],
            'año' => $row['anio'],
            'mes' => $row['mes'],
            'consumo_kwh' => $row['consumo_kwh'],
            'costo_total' => $row['costo_total'],
            'fuente_dato' => 'Carga Masiva (CSV/Excel)'
        ]);
    }

    public function rules():array {
        /**
         * Creamos las reglas para las filas
         * del Excel
         */

        return [
            'id_edificio' => 'required|integer|exists:edificio,id_edificio',
            'anio' => 'required|integer|min:2000|max:2050',
            'mes' => 'required|integer|min:1|max:12',
            'consumo_kwh' => 'required|numeric|min:0',
            'costo_total' => 'required|numeric|min:0',
        ];
    }
}
