<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateEventsBetsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up(): void
    {
        Schema::create('events_bets', function (Blueprint $table): void {
            $table->id();
            $table->decimal('amount', 10, 2);
            $table->timestamps();

            // Keys and Indexes
            $table->index('user_id');
            $table->index('choice_id');
            $table->index('event_id');

            // Foreign Key Constraints
            $table->foreignId('user_id')->references('id')->on('users');
            $table->foreignId('event_id')->references('id')->on('events');
            $table->foreignId('choice_id')->references('id')->on('events_choices');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down(): void
    {
        Schema::dropIfExists('events_bets');
    }
}