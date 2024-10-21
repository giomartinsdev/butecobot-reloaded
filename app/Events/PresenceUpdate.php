<?php

namespace App\Events;

use Discord\Discord;
use Discord\Parts\WebSockets\PresenceUpdate as DiscordPresenceUpdate;
use Discord\WebSockets\Event as Events;
use Illuminate\Support\Facades\Storage;
use Laracord\Events\Event;
use App\Models\Mongo\User as UserModel;
use App\Models\Mongo\UserStatus as UserStatusModel;
use App\Models\Mongo\UserActivity as UserActivityModel;

/**
 * DiscordPresenceUpdate json example
 * Example: {"user":{"id":"464054726997311495","username":"mecafunnie","discriminator":"0","global_name":"Meca Funnies","avatar":"https:\/\/cdn.discordapp.com\/avatars\/464054726997311495\/601a72b8cf5054c56685025a62fb9eb7.webp?size=1024","avatar_decoration":null,"bot":false,"system":null,"mfa_enabled":null,"locale":null,"verified":null,"email":null,"flags":null,"banner":null,"accent_color":null,"premium_type":null,"public_flags":0},"guild_id":"1180081513635794954","status":"online","activities":[],"client_status":{"web":"online"},"game":null,"member":{"user":{"id":"464054726997311495","username":"mecafunnie","discriminator":"0","global_name":"Meca Funnies","avatar":"https:\/\/cdn.discordapp.com\/avatars\/464054726997311495\/601a72b8cf5054c56685025a62fb9eb7.webp?size=1024","avatar_decoration":null,"bot":false,"system":null,"mfa_enabled":null,"locale":null,"verified":null,"email":null,"flags":null,"banner":null,"accent_color":null,"premium_type":null,"public_flags":0},"nick":"Meca Fun","avatar":null,"roles":[],"joined_at":"2023-12-05T01:55:33Z","premium_since":null,"deaf":false,"mute":false,"pending":false,"permissions":null,"communication_disabled_until":null,"flags":0,"guild_id":"1180081513635794954","id":"464054726997311495","status":"online","activities":[],"client_status":{"web":"online"}},"roles":[]}
 */

class PresenceUpdate extends Event
{
    /**
     * The event handler.
     *
     * @var string
     */
    protected $handler = Events::PRESENCE_UPDATE;

    /**
     * Handle the event.
     */
    public function handle(DiscordPresenceUpdate $presence, Discord $discord)
    {
        $user = UserModel::where('guild_id', $presence->guild_id)->where('discord_id', $presence->user->id)->first();

        if (!$user) {
            $newAvatarUrlQuery = parse_url($presence->user->avatar, PHP_URL_QUERY);
            $newAvatarFilename = basename($presence->user->avatar, '?' . $newAvatarUrlQuery);
            Storage::put("avatars/{$presence->user->id}/{$newAvatarFilename}", file_get_contents($presence->user->avatar));

            UserModel::create([
                'guild_id' => $presence->guild_id,
                'discord_id' => $presence->user->id,
                'username' => $presence->user->username,
                'global_name' => $presence->user->global_name,
                'avatar' => $presence->user->avatar,
                'avatar_filename' => $newAvatarFilename,
                'username_history' => [],
                'global_name_history' => [],
                'avatar_history' => [],
            ]);
        }

        $activities = collect($presence->activities)->map(function ($activity) {
            return [
                'name' => $activity->name,
                'type' => $activity->type,
                'state' => $activity->name === 'Custom Status' ? $activity->state : null,
                'emoji' => $activity->emoji ? [
                    'emoji_id' => $activity->emoji->id,
                    'name' => $activity->emoji->name,
                    'animated' => $activity->emoji->animated,
                ] : null,
            ];
        })->toArray();

        if (!empty($activities)) {
            UserActivityModel::create([
                'guild_id' => $presence->guild_id,
                'discord_id' => $presence->user->id,
                'activity_name' => $activities[0]['name'],
                'type' => $activities[0]['type'],
                'state' => $activities[0]['state'] ?? null,
                'emoji' => $activities[0]['emoji'] ?? [],
            ]);
        }

        $clientStatus = array_values(collect($presence->client_status)->map(function ($value, $name) {
            return compact('name', 'value');
        })->toArray());

        if (!empty($clientStatus)) {
            UserStatusModel::create([
                'guild_id' => $presence->guild_id,
                'discord_id' => $presence->user->id,
                'status' => $clientStatus[0]['value'],
                'client' => $clientStatus[0]['name'],
            ]);
        }
    }
}
