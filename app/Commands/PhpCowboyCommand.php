<?php

namespace App\Commands;

use Discord\Parts\Interactions\Interaction;
use Discord\Voice\VoiceClient;
use Illuminate\Support\Facades\Storage;
use Laracord\Commands\Command;

class PhpCowboyCommand extends Command
{
    /**
     * The command name.
     *
     * @var string
     */
    protected $name = 'phpcowboy';

    /**
     * The command description.
     *
     * @var string
     */
    protected $description = 'PHP, programador cowboy!';

    /**
     * Determines whether the command requires admin permissions.
     *
     * @var bool
     */
    protected $admin = false;

    /**
     * Determines whether the command should be displayed in the commands list.
     *
     * @var bool
     */
    protected $hidden = false;

    /**
     * Handle the command.
     *
     * @param  \Discord\Parts\Channel\Message  $message
     * @param  array  $args
     * @return void
     */
    public function handle($message, $args)
    {
        $audio = Storage::path('sounds/php-cowboy.mp3');
        $channel = $this->discord->getChannel($message->channel_id);
        $voice = $this->discord->getVoiceClient($channel->guild_id);

        if ($channel->isVoiceBased()) {
            if ($voice) {
                $voice->playFile($audio);
            } else {
                $this->discord->joinVoiceChannel($channel)->then(function (VoiceClient $voice) use ($audio) {
                    $voice->playFile($audio);
                });
            }

            return;
        }

        return $this
                ->message("Ihaaaa!")
                ->authorIcon('')
                ->authorName('')
                ->filePath($audio)
                ->send($message)->then(function ($message) {
                    $message->react('🤠');
                    $message->react(':php~1:1112074203735261306');
                });
    }
}
