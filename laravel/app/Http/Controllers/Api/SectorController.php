<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Sector;
use Illuminate\Http\Request;

class SectorController extends Controller
{
    /**
     * Obtiene la lista de todos los sectores.
     */
    public function index()
    {   
        $sectores = Sector::withCount('dependencias')->get();

        return response()->json($sectores);
    }
}