<?php

namespace App\Repositories;

use Illuminate\Support\Facades\DB;
use App\Models\RouletteBet;
use App\Repositories\UserCoinHistoryRepository;

class RouletteBetRepository
{
    public const OPEN = 1;
    public const CLOSED = 2;
    public const CANCELED = 3;
    public const PAID = 4;

    public const LABEL = [
        self::OPEN => 'Aberto',
        self::CLOSED => 'Fechado',
        self::CANCELED => 'Cancelado',
        self::PAID => 'Pago',
    ];

    public const LABEL_LONG = [
        self::OPEN => 'Aberto para apostas',
        self::CLOSED => 'Fechado para apostas',
        self::CANCELED => 'Cancelado',
        self::PAID => 'Apostas pagas',
    ];

    private UserCoinHistoryRepository $userCoinHistoryRepository;

    public function __construct()
    {
        $this->userCoinHistoryRepository = new UserCoinHistoryRepository;
    }

    public function createRouletteBet(int $userId, int $rouletteId, int $betAmount, int $choice) : bool
    {
        $createBetEvent = RouletteBet::create([
            'user_id' => $userId,
            'roulette_id' => $rouletteId,
            'bet_amount' => $betAmount,
            'choice' => $choice,
        ]);

        $createUserBetHistory = $this->userCoinHistoryRepository->create($userId, -$betAmount, 'RouletteBet', $rouletteId);

        return $createBetEvent && $createUserBetHistory;
    }

    public function getChoiceByRouletteIdAndKey(int $rouletteId, string $choice) : array
    {
        return RouletteBet::where('roulette_id', $rouletteId)
            ->where('choice', $choice)
            ->get()
            ->toArray();
    }

    public function getBetsByEventId(int $eventId) : array
    {
        return RouletteBet::with('user')
        ->select(
            'roulette_bet.user_id',
            'roulette_bet.choice',
            'users.discord_id',
            'users.discord_username',
            DB::raw('sum(roulette_bet.bet_amount) as amount'),
        )
        ->join('users', 'roulette_bet.user_id', '=', 'users.id')
        ->where('roulette_id', $eventId)
        ->groupBy('roulette_bet.user_id', 'roulette_bet.choice', 'users.discord_id', 'users.discord_username')
        ->get()
        ->toArray();
    }
}
