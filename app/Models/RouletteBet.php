<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class RouletteBet extends Model
{
    protected $table = 'roulette_bet';

    protected $fillable = [
        'user_id',
        'roulette_id',
        'bet_amount',
        'choice',
        'amount',
    ];

    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function roulette()
    {
        return $this->belongsTo(User::class, 'roulette_id');
    }
}