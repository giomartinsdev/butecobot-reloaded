<?php

namespace App\Events;

use Discord\Discord;
use Discord\Parts\Channel\Message;
use Discord\WebSockets\Event as Events;
use Laracord\Events\Event;
use App\Models\Mongo\Message as MessageModel;

class RecordMessage extends Event
{
    /**
     * The event handler.
     *
     * @var string
     */
    protected $handler = Events::MESSAGE_CREATE;

    /**
     * Handle the event.
     */
    public function handle(Message $message, Discord $discord)
    {
        if ($message->author->bot) {
            return;
        }

        $stickerItems = $message->sticker_items !== null ? $message->sticker_items->toArray() : [];
        $attachments = $message->attachments !== null ? $message->attachments->toArray() : [];

        if (count($stickerItems) > 0) {
            $stickerItems = array_values(
                array_map(function ($stickerItem) {
                    return [
                        'id' => $stickerItem->id,
                        'name' => $stickerItem->name,
                        'format_type' => $stickerItem->format_type,
                    ];
                }, $stickerItems)
            );
        }

        if (count($attachments) > 0) {
            $attachments = array_values(
                array_map(function ($attachment) {
                    return [
                        'id' => $attachment->id,
                        'url' => $attachment->url,
                        'type' => $attachment->content_type,
                        'filename' => $attachment->filename,
                        'size' => $attachment->size,
                    ];
                }, $attachments)
            );
        }

        MessageModel::create([
            'message_id' => $message->id,
            'discord_id' => $message->author->id,
            'channel_id' => $message->channel->id,
            'channel' => $message->channel->name,
            'username' => $message->author->username,
            'content' => $message->content,
            'history' => [],
            'emojis' => [],
            'sticker_items' => $stickerItems,
            'attachments' => $attachments,
            'deleted' => false,
        ]);
    }
}
