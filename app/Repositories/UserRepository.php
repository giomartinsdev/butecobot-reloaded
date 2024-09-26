<?php

namespace App\Repositories;

use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;
use App\Models\User;
use App\Models\UserCoinHistory;

class UserRepository
{
    public function all(): Collection
    {
        return User::all();
    }

    public function create(array $data): int
    {
        $createUser = User::create($data);

        return $createUser->id;
    }

    public function getByDiscordId(int $discordId): User|null
    {
        return User::where('discord_id', $discordId)->first();
    }

    public function getUsersByDiscordIds(array $ids): array
    {
        return User::whereIn('discord_id', $ids)->get()->toArray();
    }

    public function registerAndGiveInitialCoins(
        int $discordId,
        string $discordUsername,
        string $discordGlobalName,
        string $discordAvatar,
        string $discordJoinedAt
    ): bool
    {
        DB::beginTransaction();

        $createUser = User::create([
            'discord_id' => $discordId,
            'discord_username' => $discordUsername,
            'discord_global_name' => $discordGlobalName,
            'discord_avatar' => $discordAvatar,
            'discord_joined_at' => $discordJoinedAt,
            'received_initial_coins' => 1
        ]);

        $registerCoinsGiven = UserCoinHistory::create([
            'user_id' => $createUser->id,
            'amount' => 100,
            'type' => 'Initial'
        ]);

        if (!$createUser && !$registerCoinsGiven) {
            DB::rollback();
            return false;
        }

        DB::commit();
        return true;
    }

    public function giveCoins(int $discordId, float $amount, string $type, string $description = null): UserCoinHistory
    {
        $user = $this->getByDiscordId($discordId);

        if (empty($user)) {
            return false;
        }

        return UserCoinHistory::create([
            'user_id' => $user['id'],
            'amount' => $amount,
            'type' => $type,
            'description' => $description
        ]);
    }

    public function canReceivedDailyCoins(int $discordId): bool
    {
        $userCoinHistory = UserCoinHistory::
                                whereHas('user', function ($query) use ($discordId) {
                                    $query->where('discord_id', $discordId);
                                })
                                ->where('type', 'Daily')
                                ->whereDate('created_at', DB::raw('date(now())'))
                                ->get()->toArray();

        return empty($userCoinHistory);
    }

    public function updateReceivedInitialCoins(int $userId): bool
    {
        $user = User::find($userId);
        $user->received_initial_coins = 1;

        return $user->save();
    }

    public function getCurrentCoins(int $discordId): UserCoinHistory
    {
        return UserCoinHistory::
                    whereHas('user', function ($query) use ($discordId) {
                            $query->where('discord_id', $discordId);
                        })
                        ->selectRaw('sum(amount) as total_coins')
                        ->first();
    }

    public function hasAvailableCoins(int $discordId, int $amount): bool
    {
        $userCoinsHistory = UserCoinHistory::whereHas('user', function ($query) use ($discordId) {
                                $query->where('discord_id', $discordId);
                            })
                            ->selectRaw('sum(amount) as total')
                            ->first();

        return $userCoinsHistory['total'] >= $amount;
    }

    public function userExistByDiscordId(int $discordId): bool
    {
        $user = User::where('discord_id', $discordId)->get()->toArray();

        return !empty($user);
    }
}
