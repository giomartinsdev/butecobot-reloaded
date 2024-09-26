<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Event extends Model
{
    protected $table = 'events';

    protected $fillable = [
        'created_by',
        'winner_choice_id',
        'name',
        'status',
        'choices'
    ];

    public function choices()
    {
        return $this->hasMany(EventChoice::class, 'event_id');
    }

    public function bets()
    {
        return $this->hasMany(EventBet::class);
    }

    public function created_by()
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    public function winner_choice()
    {
        return $this->belongsTo(EventChoice::class, 'winner_choice_id');
    }
}