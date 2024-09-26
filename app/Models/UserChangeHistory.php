<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class UserChangeHistory extends Model
{
    protected $table = 'users_changes_history';

    protected $fillable = [
        'user_id',
        'info',
        'event_label',
    ];

    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }
}