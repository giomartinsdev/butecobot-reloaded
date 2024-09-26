<?php

namespace App\Repositories;

use App\Models\UserChangeHistory;

class UserChangeHistoryRepository
{
    public function create(int $userId, string $info, string $event_label): bool
    {
        return UserChangeHistory::create([
            'user_id' => $userId,
            'info' => $info,
            'event_label' => $event_label
        ]);
    }
}
