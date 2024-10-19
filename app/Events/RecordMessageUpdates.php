<?php

namespace App\Events;

use Discord\Discord;
use Discord\Parts\Channel\Message;
use Discord\WebSockets\Event as Events;
use Laracord\Events\Event;
use App\Models\Mongo\Message as MessageModel;

class RecordMessageUpdates extends Event
{
    /**
     * The event handler.
     *
     * @var string
     */
    protected $handler = Events::MESSAGE_UPDATE;

    /**
     * Handle the event.
     */
    public function handle(Message $message, Discord $discord, ?Message $oldMessage)
    {
        if ($message->author->bot) {
            return;
        }

        $message = MessageModel::where('message_id', $message->id)->first();
        $history = array_merge($message->history ?? [], [ $oldMessage->content ]);
        $message->content = $message->content;
        $message->history = $history;
        $message->save();
    }
}
