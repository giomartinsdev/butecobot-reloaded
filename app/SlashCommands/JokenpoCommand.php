<?php

namespace App\SlashCommands;

use Discord\Parts\Interactions\Interaction;
use Laracord\Commands\SlashCommand;
use Illuminate\Support\Facades\Redis;
use App\Repositories\UserRepository;
use App\Entities\JokenpoEntity;
use App\Models\Jokenpo;
use App\SlashCommands\Traits\Jokenpo\PlayJokenpo;

class JokenpoCommand extends SlashCommand
{
    use PlayJokenpo;

    /**
     * The command name.
     *
     * @var string
     */
    protected $name = 'jokenpo';

    /**
     * The command description.
     *
     * @var string
     */
    protected $description = 'Pedra, papel, tesoura, lagarto, spock... frenético!';

    /**
     * The command options.
     *
     * @var array
     */
    protected $options = [];

    /**
     * The permissions required to use the command.
     *
     * @var array
     */
    protected $permissions = [];

    /**
     * Indicates whether the command requires admin permissions.
     *
     * @var bool
     */
    protected $admin = false;

    /**
     * Indicates whether the command should be displayed in the commands list.
     *
     * @var bool
     */
    protected $hidden = false;

    /**
     * The game instance.
     *
     * @var JokenpoEntity|null
     */
    protected ?JokenpoEntity $game = null;

    /**
     * Game timer counter.
     *
     * @var int
     */
    protected int $counter = 0;

    /**
     * Handle the slash command.
     *
     * @param  \Discord\Parts\Interactions\Interaction  $interaction
     * @return mixed
     */
    public function handle($interaction)
    {
        $userRepository = new UserRepository;
        $user = $userRepository->getByDiscordId($interaction->member->user['id']);
        $newGame = Jokenpo::create([
            'created_by' => $user['id'],
        ]);
        $game = Redis::get("jokenpo:game:{$newGame['id']}");

        if ($game) {
            $game = unserialize($game);
        } else {
            $game = new JokenpoEntity($newGame['id']);
        }

        $this->game = $game;

        $interaction->respondWithMessage(
            $this->buildGameMessage()
        )->then(fn() => $this->startCounter($interaction));
    }

    /**
     * The command interaction routes.
     */
    public function interactions() : array
    {
        return [
            'action:{type}' => fn (Interaction $interaction, string $type) => $this->playJokenpo($interaction, $type),
        ];
    }

    public function startCounter(Interaction $interaction)
    {
        $this->counter = env('JOKENPO_TIMER', 30);

        $timer = $this->bot->getLoop()->addPeriodicTimer(1, function () use (&$timer, $interaction) {
            if ($this->counter === 0) {
                $this->bot->getLoop()->cancelTimer($timer);
                $this->counter = env('JOKENPO_TIMER', 30);
                $this->game->setBotMove();

                Redis::del("jokenpo:game:{$this->game->getId()}");
                Jokenpo::find($this->game->getId())->update([
                    'bot_move' => $this->game->getBotMove(),
                ]);

                $interaction->updateOriginalResponse(
                    $this->buildGameResults()
                );
                return;
            }

            $interaction->updateOriginalResponse(
                $this->buildGameMessage()
            );

            $this->counter--;
        });
    }
}
