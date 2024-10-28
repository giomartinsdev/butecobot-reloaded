<?php

namespace App\Commands;

use Discord\Parts\Interactions\Interaction;
use Illuminate\Support\Facades\Storage;
use Laracord\Commands\Command;

class AdviceCommand extends Command
{
    /**
     * The command name.
     *
     * @var string
     */
    protected $name = 'conselho';

    /**
     * The command description.
     *
     * @var string
     */
    protected $description = 'Quer um conselho?';

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
        $mention = $this->extractDiscordMention($args[0] ?? '');
        $mentionString = $mention ? "Hey <@{$mention}>" : "Ei você";

        return $this
            ->message("{$mentionString}, depois dessa lapada aí em cima que tal ver o vídeo completo?")
            ->authorIcon('')
            ->authorName('')
            ->filePath(Storage::path('videos/akita-nao-terceirize.mp4'))
            ->button('Vídeo completo', 'https://www.youtube.com/watch?v=D3L8IOncLkg', emoji: '▶️')
            ->send($message);
    }

    private function extractDiscordMention($string) {
        $pattern = '/<@(\d+)>/';

        if (preg_match($pattern, $string, $matches)) {
            return $matches[1];
        }

        return null;
    }
}
