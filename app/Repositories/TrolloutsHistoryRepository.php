<?php

namespace App\Repositories;

use Illuminate\Support\Facades\DB;
use App\Models\TrolloutHistory;
use App\Repositories\UserRepository;

class TrolloutsHistoryRepository
{
    private UserRepository $userRepository;

    public function __construct()
    {
        $this->userRepository = new UserRepository;
    }

    public function create(string $userId, string $toId): bool
    {
        DB::beginTransaction();

        $users = $this->userRepository->getByDiscordId($userId);

        if (empty($users)) {
            return false;
        }

        $userFrom = $users[0];
        $users = $this->userRepository->getByDiscordId($toId);

        if (empty($users)) {
            return false;
        }

        $trollout = TrolloutHistory::create([
            'user_id' => $userFrom['id'],
            'to_id' => $users[0]['id'],
        ]);

        DB::commit();

        return $trollout;
    }
}