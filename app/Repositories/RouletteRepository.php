<?php

namespace App\Repositories;

use App\Models\Roulette;
use App\Repositories\RouletteBetRepository;
use App\Repositories\UserRepository;
use App\Repositories\UserCoinHistoryRepository;

class RouletteRepository
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

    public const GREEN = 1;
    public const BLACK = 2;
    public const RED = 3;

    public const GREEN_MULTIPLIER = 14;
    public const BLACK_MULTIPLIER = 2;
    public const RED_MULTIPLIER = 2;

    public const LABEL_CHOICE = [
        self::GREEN => 'VERDE',
        self::BLACK => 'PRETO',
        self::RED => 'VERMELHO',
    ];

    private RouletteBetRepository $rouletteBetRepository;
    private UserRepository $userRepository;
    private UserCoinHistoryRepository $userCoinHistoryRepository;

    public function __construct()
    {
        $this->rouletteBetRepository = new RouletteBetRepository;
        $this->userRepository = new UserRepository;
        $this->userCoinHistoryRepository = new UserCoinHistoryRepository;
    }

    public function createEvent(string $eventName, int $value, int $discordId): int|bool
    {
        $user = $this->userRepository->getByDiscordId($discordId);
        $userId = $user['id'];

        $createEvent = Roulette::create([
            'created_by' => $userId,
            'status' => self::OPEN,
            'description' => $eventName,
            'amount' => $value,
        ]);

        return $createEvent ? $createEvent->id : false;
    }

    public function close(int $eventId): bool
    {
        $roulette = Roulette::find($eventId);
        $roulette->status = self::CLOSED;
        return $roulette->save();
    }

    public function finish(int $eventId): bool
    {
        $roulette = Roulette::find($eventId);
        $roulette->status = self::PAID;
        return $roulette->save();
    }

    public function listEventsOpen(int $limit = null): array
    {
        $data = $this->normalizeRoulette($this->listEventsByStatus([self::OPEN], $limit));

        return $data;
    }

    public function listEventsClosed(int $limit = null): array
    {
        return $this->normalizeRoulette($this->listEventsByStatus([self::CLOSED], $limit));
    }

    public function listEventsPaid(int $limit = null): array
    {
        return $this->normalizeRoulette($this->listEventsByStatus([self::PAID], $limit));
    }

    public function listEventsByStatus(array $status, int $limit = null): array
    {
        $roulette = Roulette::
                        whereIn('status', $status)
                        ->when($limit, function ($query) use ($limit) {
                            return $query->limit($limit);
                        })
                        ->orderBy('id', 'DESC')
                        ->get()
                        ->toArray();
        return $roulette;
    }

    public function normalizeRoulette(array $roulette): array
    {
        return array_map(function ($item) {
            return [
                'id' => $item['id'],
                'description' => $item['description'],
                'amount' => $item['amount'],
                'result' => $item['result'],
                'status' => $item['status'],
            ];
        }, $roulette);
    }

    public function getRouletteById(int $rouletteId): Roulette
    {
        return Roulette::find($rouletteId);
    }

    public function closeEvent(int $rouletteId): bool
    {
        $roulette = Roulette::find($rouletteId);
        $roulette->status = self::CLOSED;
        return $roulette->save();
    }

    public function payoutRoulette(int $rouletteId, $winnerNumber): array
    {
        $winners = [];
        $bets = $this->rouletteBetRepository->getBetsByEventId($rouletteId);
        $choiceData = $this->getWinnerChoiceByNumber($winnerNumber);
        $odd = 2;

        if ($choiceData['choice'] === self::GREEN) {
            $odd = 14;
        }

        $this->updateRouletteWithWinner($winnerNumber, $rouletteId);

        foreach ($bets as $bet) {
            if ($bet['choice'] !== $choiceData['choice']) {
                continue;
            }

            $betPayout = $bet['amount'] * $odd;
            $winners[] = [
                'discord_id' => $bet['discord_id'],
                'discord_username' => $bet['discord_username'],
                'choice' => $bet['choice'],
                'earnings' => $betPayout,
            ];

            $this->userCoinHistoryRepository->create($bet['user_id'], $betPayout, 'RouletteBet', $rouletteId);
        }

        return $winners;
    }

    public function updateRouletteWithWinner(int $winnerNumber, int $eventId): bool
    {
        $roulette = Roulette::find($eventId);
        $roulette->status = self::PAID;
        $roulette->result = $winnerNumber;
        return $roulette->save();
    }

    public function getWinnerChoiceByNumber(int $number): array
    {
        if ($number == 0) {
            $winnerChoice = self::GREEN;
            $labelChoice = "🟩 G[$number]";
        } elseif ($number % 2 == 0) {
            $winnerChoice = self::BLACK;
            $labelChoice = "⬛ BL[$number]";
        } else {
            $winnerChoice = self::RED;
            $labelChoice = "🟥 R[$number]";
        }

        return [
            'choice' => $winnerChoice,
            'label' => $labelChoice,
        ];
    }
}
