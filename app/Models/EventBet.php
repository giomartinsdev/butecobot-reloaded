<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class EventBet extends Model
{
    protected $table = 'events_bets';

    protected $fillable = [
        'user_id',
        'event_id',
        'choice_id',
        'amount',
    ];

    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function event()
    {
        return $this->belongsTo(Event::class, 'event_id');
    }

    public function event_choice()
    {
        return $this->belongsTo(EventChoice::class, 'choice_id');
    }
}