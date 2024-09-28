<?php

namespace App\Repositories;

use Illuminate\Database\Eloquent\Collection;
use App\Models\EventChoice;

class EventChoiceRepository
{
    public function all() : Collection
    {
        return EventChoice::all();
    }

    public function getByEventAndChoice(int $eventId, string $choice) : ?EventChoice
    {
        return EventChoice::where('event_id', $eventId)
            ->where('choice', $choice)
            ->first();
    }
}
