<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Sector extends Model
{
    use HasFactory;

    protected $table = 'sector';
    protected $primaryKey = 'id_sector';
    public $timestamps = false;

    protected $fillable = [
        'nombre_sector', 
        'descripcion'
    ];

    public function dependencias () {
        return $this->hasMany(Dependencia::class, 'sector_id', 'sector_id');
    }
}
