<?php

namespace App\Helpers;

class StringHelper
{
    public static function formatMoney(int|float $amount): string
    {
        if ($amount >= 1000000) {
            $formatted_amount = number_format($amount / 1000000, 2) . "M";
        } elseif ($amount >= 1000) {
            $formatted_amount = number_format($amount / 1000, 2) . "K";
        } else {
            $formatted_amount = number_format($amount, 2);
        }

        return $formatted_amount;
    }

    public static function isLinkLongerThan(string $string, $length): bool
    {
        $urlPattern = '/https?:\/\/[^\s]+/i';
        preg_match($urlPattern, $string, $match);

        if (isset($match[0]) && strlen($match[0]) > $length) {
            return $match[0];
        }

        return false;
    }
}
