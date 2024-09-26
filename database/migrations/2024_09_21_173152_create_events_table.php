<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateEventsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up(): void
    {
        Schema::create('events', function (Blueprint $table): void {
            $table->id();
            // $table->bigInteger('winner_choice_id');
            $table->string('name', 255);
            $table->tinyInteger('status');
            $table->timestamps();

            // Keys and Indexes
            $table->index('created_by');

            // Foreign Key Constraints
            $table->foreignId('created_by')->references('id')->on('users');
        });

        Schema::create('events_choices', function (Blueprint $table): void {
            $table->id();
            $table->string('choice', 255);
            $table->string('description', 255);
            $table->timestamps();

            // Keys and Indexes
            $table->index('event_id');

            // Foreign Key Constraints
            $table->foreignId('event_id')->references('id')->on('events');
        });

        Schema::table('events', function (Blueprint $table): void {
            $table->foreignId('winner_choice_id')->nullable()->after('id')
                    ->references('id')->on('events_choices');
            $table->index('winner_choice_id');
        });

    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down(): void
    {
        Schema::dropIfExists('events_choices');
        Schema::dropIfExists('events');
    }
}