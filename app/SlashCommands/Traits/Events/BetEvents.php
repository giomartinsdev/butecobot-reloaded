<?php

namespace App\SlashCommands\Traits\Events;

use Laracord\Commands\SlashCommand;
use App\Repositories\EventRepository;
use App\Repositories\EventBetRepository;
use App\Repositories\UserRepository;

/**
 * @mixin SlashCommand
 */
trait BetEvents
{
    /**
     * Handle the slash command.
     *
     * @param  \Discord\Parts\Interactions\Interaction  $interaction
     * @return mixed
     */
    public function betEvent($interaction)
    {
        $userRepository = new UserRepository;
        $eventRepository = new EventRepository;
        $eventBetRepository = new EventBetRepository;
        $betEventId = $this->value('apostar.evento');
        $betChoice = $this->value('apostar.opcao');
        $betAmount = $this->value('apostar.valor');
        $discordId = $interaction->member->user->id;
        $event = $eventRepository->getEventById($betEventId);
        $user = $userRepository->getByDiscordId($discordId);

        if (!$user) {
            $interaction->respondWithMessage(
                $this->message('Você ainda não coleteu suas coins iniciais! Digita **/coins** e pegue suas coins! :coin::coin::coin:')
                    ->title('Eventos')
                    ->build(),
                true
            );
            return;
        }

        if (!$event) {
            $interaction->respondWithMessage(
                $this->message("Evento **#{$betEventId}** não existe")
                ->title('Eventos')
                ->build(),
                true
            );
            return;
        }

        if ($event['status'] !== EventRepository::OPEN) {
            $interaction->respondWithMessage(
                $this->message('Evento fechado para apostas!')
                ->title('Eventos')
                ->build(),
                true
            );
            return;
        }

        if ($eventBetRepository->didUserBet($discordId, $betEventId)) {
            $interaction->respondWithMessage(
                $this->message('Você já apostou neste evento!')
                ->title('Eventos')
                ->build(),
                true
            );
            return;
        }

        if ($betAmount <= 0) {
            $interaction->respondWithMessage(
                $this->message('Valor da aposta inválido, o valor deve ser acima de 0')
                ->title('Aposta')
                ->build(),
                true
            );
            return;
        }

        if (!$userRepository->hasAvailableCoins($discordId, $betAmount)) {
            $interaction->respondWithMessage(
                $this->message('Você não possui coins suficientes!')
                ->title('Eventos')
                ->build(),
                true
            );
            return;
        }

        $bet = $eventBetRepository->create($discordId, $betEventId, $betChoice, $betAmount);
        $choiceDetails = array_filter(
            $event['choices']->toArray(),
            fn ($item) => $item['choice'] === $betChoice
        );

        if ($bet) {
            $interaction->respondWithMessage(
                $this->message(sprintf(
                        "**%s**\nOpção: **%s - %s**\nValor apostado: **%s** coins",
                        $event['name'],
                        $betChoice,
                        $choiceDetails[0]['description'],
                        $betAmount,
                        $betChoice
                ))
                ->title('Eventos')
                ->color('#F5D920')
                ->thumbnail(config('butecobot.images.place_bet'))
                ->build(),
                true
            );
        }
    }
}
