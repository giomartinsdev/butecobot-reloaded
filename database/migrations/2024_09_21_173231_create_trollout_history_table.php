<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateTrolloutHistoryTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up(): void
    {
        Schema::create('trollout_history', function (Blueprint $table): void {
            $table->id();
            $table->timestamps();

            // Keys and Indexes
            $table->index('user_id');
            $table->index('to_id');

            // Foreign Key Constraints
            $table->foreignId('user_id')->references('id')->on('users');
            $table->foreignId('to_id')->references('id')->on('users');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down(): void
    {
        Schema::dropIfExists('trollout_history');
    }
}