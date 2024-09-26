<?php

namespace App\Repositories;

use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;
use App\Models\EventBet;
use App\Repositories\UserRepository;
use App\Repositories\EventRepository;
use App\Repositories\EventChoiceRepository;
use App\Repositories\UserCoinHistoryRepository;

class EventBetRepository
{
    private UserRepository $userRepository;
    private EventChoiceRepository $eventChoiceRepository;
    private UserCoinHistoryRepository $userCoinHistoryRepository;

    public function __construct()
    {
        $this->userRepository = new UserRepository;
        $this->eventChoiceRepository = new EventChoiceRepository;
        $this->userCoinHistoryRepository = new UserCoinHistoryRepository;
    }

    public function all(): Collection
    {
        return EventBet::all();
    }

    public function create(int $discordId, int $eventId, string $choice, float $amount): bool
    {
        try {
            $eventRepository = new EventRepository;
            $user = $this->userRepository->getByDiscordId($discordId);
            $userId = $user['id'];
            $choice = $this->eventChoiceRepository->getByEventAndChoice($eventId, $choice);
            $odds = $eventRepository->calculateOdds($eventId);

            DB::beginTransaction();

            EventBet::create([
                'user_id' => $userId,
                'event_id' => $eventId,
                'choice_id' => $choice['id'],
                'amount' => $amount,
            ]);

            $this->userCoinHistoryRepository->create(
                $userId,
                -$amount,
                'EventBet',
                $eventId,
                json_encode([
                    'betted' => $amount,
                    'choice' => $choice['description'],
                    'odds' => $choice === 'A' ? $odds['odds_a'] : $odds['odds_b'],
                ])
            );

            DB::commit();

            return true;
        } catch (\Exception $e) {
            DB::rollback();
            return false;
        }
    }

    public function getUserOpenBets(int $userId, int $eventId): Collection
    {
        return EventBet::whereHas('event', function ($query) {
            $query->where('status', EventRepository::OPEN);
        })
        ->where('user_id', $userId)
        ->where('event_id', $eventId)
        ->get();
    }

    public function didUserBet(int $discordId, int $eventId): bool
    {
        $user = $this->userRepository->getByDiscordId($discordId);

        return $this->getUserOpenBets($user['id'], $eventId)->count() > 0;
    }

    public function getBetsByEventId(int $eventId): array
    {
        return EventBet::with('user', 'event_choice')
            ->where('event_id', $eventId)
            ->get()
            ->toArray();
    }
}
