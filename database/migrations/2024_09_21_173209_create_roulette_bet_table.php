<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateRouletteBetTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up(): void
    {
        Schema::create('roulette_bet', function (Blueprint $table): void {
            $table->id();
            $table->integer('bet_amount')->nullable();
            $table->integer('choice')->nullable();
            $table->timestamps();

            // Keys and Indexes
            $table->index('user_id');
            $table->index('roulette_id');

            // Foreign Key Constraints
            $table->foreignId('user_id')->references('id')->on('users');
            $table->foreignId('roulette_id')->references('id')->on('roulette');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down(): void
    {
        Schema::dropIfExists('roulette_bet');
    }
}