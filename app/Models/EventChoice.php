<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class EventChoice extends Model
{
    protected $table = 'events_choices';

    protected $fillable = [
        'event_id',
        'choice',
        'description',
    ];

    public function event()
    {
        return $this->belongsTo(Event::class, 'event_id');
    }
}