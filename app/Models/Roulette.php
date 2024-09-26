<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Roulette extends Model
{
    protected $table = 'roulette';

    protected $fillable = [
        'created_by',
        'result',
        'status',
        'description',
        'amount',
    ];

    public function created_by()
    {
        return $this->belongsTo(User::class, 'created_by');
    }
}