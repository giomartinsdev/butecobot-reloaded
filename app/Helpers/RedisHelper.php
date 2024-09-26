<?php

namespace App\Helpers;

use Illuminate\Support\Facades\Redis;

class RedisHelper
{
    public static function cooldown(string $key, int $seconds = 60, int $times = 2): bool
    {
        if ($curThreshold = Redis::get($key)) {
            if ($curThreshold < $times) {
                Redis::set($key, ++$curThreshold, 'EX', $seconds);
                return true;
            }
            return false;
        }

        Redis::set($key, 1, 'EX', $seconds);
        return true;
    }
}