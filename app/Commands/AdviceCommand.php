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
        return $this
            ->message("Hey <@{$message->author->id}>, depois dessa lapada aí em cima que tal ver o vídeo completo? Vídeo completo: https://www.youtube.com/watch?v=D3L8IOncLkg")
            ->authorIcon('')
            ->authorName('')
            ->filePath(Storage::path('videos/akita-nao-terceirize.mp4'))
            ->send($message);
    }

    /**
     * The command interaction routes.
     */
    public function interactions(): array
    {
        return [
            'wave' => fn (Interaction $interaction) => $this->message('👋')->reply($interaction), 
        ];
    }
}
