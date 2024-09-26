<?php

namespace App\SlashCommands\Traits\Events;

use Laracord\Commands\SlashCommand;
use App\Repositories\EventRepository;

/**
 * @mixin SlashCommand
 */
trait EndEvents
{
    /**
     * Handle the slash command.
     *
     * @param  \Discord\Parts\Interactions\Interaction  $interaction
     * @return mixed
     */
    public function endEvent($interaction)
    {
        $eventRepository = new EventRepository;
        $eventId = $this->value('encerrar.evento');
        $choiceLabel = $this->value('encerrar.opcao');
        $event = $eventRepository->getEventById($eventId);

        if (!$event) {
            $interaction->respondWithMessage(
                $this->message('Evento não existe')
                    ->title('Eventos')
                    ->build(),
                true
            );
            return;
        }

        if ($event['status'] == EventRepository::PAID) {
            $interaction->respondWithMessage(
                $this->message('Este evento já foi pago!')
                    ->title('Eventos')
                    ->build(),
                true
            );
            return;
        }

        if ($event['status'] !== EventRepository::CLOSED) {
            $interaction->respondWithMessage(
                $this->message('Evento precisa estar fechado para ser finalizado!')
                    ->title('Eventos')
                    ->build(),
                true
            );
            return;
        }

        if ($choiceLabel === 'Empate') {
            if (!$eventRepository->drawEvent($eventId)) {
                $interaction->respondWithMessage(
                    $this->message('Erro ao encerrar evento')
                        ->title('Eventos')
                        ->build(),
                    true
                );
                return;
            }

            $interaction->respondWithMessage(
                $this->message(sprintf("Evento: #%s %s\nResultado: Empate!\n\nApostas devolvidas", $eventId, $event['name']))
                    ->title('Eventos')
                    ->build(),
                false
            );
            return;
        }

        $winners = $eventRepository->payoutEvent($eventId, $choiceLabel);

        if (count($winners) === 0) {
            $interaction->respondWithMessage($this->messageComposer->embed(
                'Evento',
                'Não houveram apostas neste evento!'
            ), false);
            return;
        }

        $winnersImage = config('butecobot.images.winners')[array_rand(config('butecobot.images.winners'))];
        $winnersLabel = '';
        $earningsLabel = '';

        foreach ($winners as $winner) {
            if ($winner['choice'] == $choiceLabel) {
                $winnersLabel .= sprintf("<@%s> \n", $winner['discord_id']);
                $earningsLabel .= sprintf("%s %s \n", $winner['earnings'], $winner['extraLabel']);
            }
        }

        $eventsDescription = sprintf(
            "**%s** \n **Vencedor**: %s \n \n \n",
            $event['name'],
            $choiceLabel,
        );

        $interaction->respondWithMessage(
            $this->message($eventsDescription)
                ->title('Eventos')
                ->color('#F5D920')
                ->fields([
                    'Ganhador' => $winnersLabel,
                    'Valor' => $earningsLabel
                ])
                ->image($winnersImage)
                ->build()
        );
    }
}
