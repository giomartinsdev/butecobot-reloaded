<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class UserCoinHistory extends Model
{
    protected $table = 'users_coins_history';

    protected $fillable = [
        'user_id',
        'entity_id',
        'amount',
        'type',
        'description',
    ];

    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }
}