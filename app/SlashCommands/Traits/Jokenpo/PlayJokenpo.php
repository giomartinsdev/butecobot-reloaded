<?php

namespace App\SlashCommands\Traits\Jokenpo;

use Discord\Builders\MessageBuilder;
use Discord\Parts\Interactions\Interaction;
use Illuminate\Support\Facades\Redis;
use Laracord\Commands\SlashCommand;
use App\Entities\JokenPoEntity;
use App\Entities\JokenPoPlayerEntity;
use App\Models\JokenpoPlayer;
use App\Repositories\UserCoinHistoryRepository;
use App\Repositories\UserRepository;

/**
 * @mixin SlashCommand
 * @property JokenPoEntity $game
 */
trait PlayJokenpo
{
    /**
     * @param  \Discord\Parts\Interactions\Interaction  $interaction
     * @param  string  $type
     * @return void
     */
    public function playJokenpo(Interaction $interaction, string $type) : void
    {
        $discordId = $interaction->member->user->id;
        $userCoinHistoryRepository = new UserCoinHistoryRepository;
        $userRepository = new UserRepository;

        if ($userCoinHistoryRepository->hasAvailableCoins($discordId, 200.0) === false) {
            $interaction->respondWithMessage(
                $this
                ->message('Você não tem coins suficientes para jogar!')
                ->build(),
                true
            );
            return;
        }

        $playerMove = $this->game->setPlayerMove(new JokenPoPlayerEntity($discordId, $type));

        if (!$playerMove) {
            $interaction->respondWithMessage(
                $this
                ->message('Você já fez sua jogada!')
                ->build(),
                true
            );
            return;
        }

        Redis::set("jokenpo:game:" . $this->game->getId(), serialize($this->game));
        $userCoinHistoryRepository->spendCoins(
            $discordId,
            -200,
            'Jokenpo',
            [
                'game_id' => $this->game->getId(),
                'move' => $type,
            ]
        );
        JokenpoPlayer::create([
            'jokenpo_id' => $this->game->getId(),
            'user_id' => $userRepository->getByDiscordId($discordId)['id'],
            'move' => $type,
            'amount' => 200,
        ]);

        $interaction->updateMessage(
            $this->buildGameMessage($interaction)
        );
    }

    /**
     * @return \Discord\Builders\MessageBuilder
     */
    public function buildGameMessage() : MessageBuilder
    {
        $players = implode("\n", array_map(fn($player) => sprintf("<@%s>", $player->getDiscordId()), $this->game->getPlayers()));
        $choices = implode("\n", array_map(fn($player) => sprintf("%s %s", $this->game->getEmoji($player->getMove()), ucwords($player->getMove())), $this->game->getPlayers()));

        return $this
        ->message(sprintf("Ado, ado, ado quem perder é...ruim!\n\n⏰: **%s**", $this->counter))
        ->title('JO-KEN-PÔ!')
        ->fields([
            'Jogador' => $players,
            'Escolheu' => $choices,
        ])
        ->button("Pedra", route: 'action:pedra', style: 'secondary', emoji: $this->game->getEmoji('pedra'))
        ->button("Papel", route: 'action:papel', style: 'secondary', emoji: $this->game->getEmoji('papel'))
        ->button("Tesoura", route: 'action:tesoura', style: 'secondary', emoji: $this->game->getEmoji('tesoura'))
        ->button("Lagarto", route: 'action:lagarto', style: 'secondary', emoji: $this->game->getEmoji('lagarto'))
        ->button("Spock", route: 'action:spock', style: 'secondary', emoji: $this->game->getEmoji('spock'))
        ->build();
    }

    /**
     * @return \Discord\Builders\MessageBuilder
     */
    public function buildGameResults() : MessageBuilder
    {
        $userCoinHistoryRepository = new UserCoinHistoryRepository;
        $userRepository = new UserRepository;
        $evaluatedPlayers = $this->game->evaluateMoves();
        $players = implode("\n", array_map(fn($player) => sprintf("<@%s>", $player->getDiscordId()), $this->game->getPlayers()));
        $choices = implode("\n", array_map(fn($player) => sprintf("%s %s", $this->game->getEmoji($player->getMove()), $player->getMove()), $this->game->getPlayers()));
        $results = implode("\n", array_map(fn($player) => ucwords($player->getResult()), $evaluatedPlayers));

        // TODO: Refactor this to a repository
        array_map(function ($player) use ($userRepository, $userCoinHistoryRepository) {
            JokenpoPlayer::where('jokenpo_id', $this->game->getId())
                ->where('user_id', $userRepository->getByDiscordId($player->getDiscordId())['id'])
                ->update(['result' => $player->getResult()]);

            if ($player->getResult() === 'ganhou') {
                $userCoinHistoryRepository->spendCoins(
                    $player->getDiscordId(),
                    400,
                    'Jokenpo',
                    [
                        'game_id' => $this->game->getId(),
                        'move' => $player->getMove(),
                        'result' => $player->getResult(),
                        'bot_move' => $this->game->getBotMove(),
                    ]
                );
                return;
            }
        }, $evaluatedPlayers);

        return $this
        ->message(
            sprintf(
                "Eu escolhi: **%s**\n\n\n",
                sprintf("%s %s", $this->game->getEmoji($this->game->getBotMove()), ucwords($this->game->getBotMove()))
            )
        )
        ->title('JO-KEN-PÔ!')
        ->fields([
            'Jogador' => $players,
            'Escolheu' => $choices,
            'Resultado' => $results,
        ])
        ->build();
    }
}