<?php

namespace App\SlashCommands\Traits\Events;

use Laracord\Commands\SlashCommand;
use App\Repositories\EventRepository;

/**
 * @mixin SlashCommand
 */
trait CreateEvents
{
    /**
     * Handle the slash command.
     *
     * @param  \Discord\Parts\Interactions\Interaction  $interaction
     * @return mixed
     */
    public function createEvent($interaction): void
    {
        $eventRepository = new EventRepository;
        $discordId = $interaction->member->user->id;
        $eventName = $this->value('criar.nome');
        $optionA = $this->value('criar.a');
        $optionB = $this->value('criar.b');

        $eventRepository->create(strtoupper($eventName), $optionA, $optionB, $discordId);
        $interaction->respondWithMessage(
            $this->message('Evento criado com sucesso!')
                ->title('Eventos')
                ->build(),
            true
        );
    }
}
