<?php
namespace App\Models\Mongo;

use MongoDB\Laravel\Eloquent\Model;

class UserActivity extends Model
{
    protected $connection = 'mongodb';

    protected $fillable = [
        'guild_id',
        'discord_id',
        'application_id',
        'activity_type',
        'state',
        'emoji',
    ];
}