<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Talk extends Model
{
    protected $table = 'talks';

    protected $fillable = [
        'trigger_text',
        'type',
        'answer',
        'status',
    ];
}