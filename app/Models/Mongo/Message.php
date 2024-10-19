<?php
namespace App\Models\Mongo;

use MongoDB\Laravel\Eloquent\Model;

class Message extends Model
{
    protected $connection = 'mongodb';

    protected $fillable = [
        'message_id',
        'discord_id',
        'channel_id',
        'channel',
        'username',
        'content',
        'history',
        'emojis',
        'sticker_items',
        'attachments',
        'deleted',
    ];
}