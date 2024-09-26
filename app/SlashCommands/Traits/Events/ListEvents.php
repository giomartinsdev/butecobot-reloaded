<?php

namespace App\SlashCommands\Traits\Events;

use Discord\Parts\Interactions\Interaction;
use Laracord\Commands\SlashCommand;
use App\Repositories\EventRepository;

/**
 * @mixin SlashCommand
 */
trait ListEvents
{
    /**
     * List of Events
     * @var Collection
     */
    protected $listEventsEvents = [];

    /**
     * List of Events
     * @var int
     */
    protected $listEventsCurrentPage = 0;

    /**
     * Handle the slash command.
     *
     * @param  Interaction  $interaction
     * @return mixed
     */
    public function listEvents($interaction): void
    {
        $eventsRepository = new EventRepository;
        $eventsOpen = $eventsRepository->listEventsOpen();
        $eventsClosed = $eventsRepository->listEventsClosed();
        $this->listEventsEvents = $eventsOpen->merge($eventsClosed);
        $this->listEventsCurrentPage = 0;

        if ($this->listEventsEvents->isEmpty()) {
            $interaction->respondWithMessage(
                $this->message('Nenhum evento encontrado')
                    ->title('Eventos')
                    ->build(),
                true
            );
            return;
        }

        $interaction->acknowledgeWithResponse(true)->then(
            fn() =>  $interaction->updateOriginalResponse($this->listEventsBuildMessage())
        );
    }

    public function listEventsBackward(Interaction $interaction)
    {
        if (($this->listEventsCurrentPage - 1) === -1) {
            $interaction->acknowledge();
            return;
        }

        $this->listEventsCurrentPage -= 1;

        $interaction->updateMessage($this->listEventsBuildMessage());
    }

    public function listEventsForward(Interaction $interaction)
    {
        if (($this->listEventsCurrentPage + 1) === $this->listEventsEvents->count()) {
            $interaction->acknowledge();
            return;
        }

        $this->listEventsCurrentPage += 1;

        $interaction->updateMessage($this->listEventsBuildMessage());
    }

    public function listEventsBuildMessage()
    {
        $eventsRepository = new EventRepository;
        $event = $this->listEventsEvents[$this->listEventsCurrentPage];
        $eventOdds = $eventsRepository->calculateOdds($event['id']);
        $statusIcon = match($event['status']) {
            $eventsRepository::CLOSED => '🔴',
            default => '🟢',
        };
        $eventsDescription = sprintf(
            "**%s** \n **%s %s** \n\n **A**: %s \n **B**: %s",
            strtoupper($event['name']),
            $statusIcon,
            $eventsRepository::LABEL_LONG[(int) $event['status']],
            sprintf('%s (x%s)', $event['choices'][0]['description'], number_format($eventOdds['odds_a'], 2)),
            sprintf('%s (x%s)', $event['choices'][1]['description'], number_format($eventOdds['odds_b'], 2))
        );

        return $this->message($eventsDescription)
                    ->title(sprintf('Evento **#%s**', $event['id']))
                    ->color('#F5D920')
                    ->thumbnail(config('images.event'))
                    ->button('<', route: 'list:backward')
                    ->button('>', route: 'list:forward')
                    ->footerText(sprintf(
                        'Página %s de %s',
                        $this->listEventsCurrentPage + 1,
                        $this->listEventsEvents->count()
                    ))
                    ->build();
    }
}
