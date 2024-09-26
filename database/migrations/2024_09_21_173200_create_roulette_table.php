<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateRouletteTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up(): void
    {
        Schema::create('roulette', function (Blueprint $table): void {
            $table->id();
            $table->integer('result')->nullable();
            $table->integer('status')->default(0);
            $table->string('description', 255)->nullable();
            $table->decimal('amount', 10, 2)->nullable();
            $table->timestamps();

            // Keys and Indexes
            $table->index('created_by');

            // Foreign Key Constraints
            $table->foreignId('created_by')->references('id')->on('users');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down(): void
    {
        Schema::dropIfExists('roulette');
    }
}