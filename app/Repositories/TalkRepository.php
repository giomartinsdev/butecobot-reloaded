<?php

namespace App\Repositories;

use App\Models\Talk;

class TalkRepository
{
    public const STATUS_ACTIVE = 1;
    public const STATUS_INACTIVE = 0;

    public function create(string $triggertext, string $type, string $answer) : bool
    {
        return Talk::create([
            'triggertext' => $triggertext,
            'type' => $type,
            'answer' => $answer,
            'status' => self::STATUS_ACTIVE
        ]);
    }

    public function findById(int $id) : Talk
    {
        return Talk::find($id);
    }

    public function findTrigger(string $triggertext) : array
    {
        return Talk::where('triggertext', $triggertext)
            ->where('status', self::STATUS_ACTIVE)
            ->get()
            ->toArray();
    }

    public function listAllTriggers() : array
    {
        return Talk::where('status', self::STATUS_ACTIVE)
            ->get()
            ->toArray();
    }
}
