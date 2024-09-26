<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TrolloutHistory extends Model
{
    protected $table = 'trollout_history';

    protected $fillable = [
        'user_id',
        'to_id',
    ];

    public function from()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function to()
    {
        return $this->belongsTo(User::class, 'to_id');
    }
}