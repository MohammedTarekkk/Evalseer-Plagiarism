<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class BadgeController extends Controller
{
    public function view() {
        return view('badges');
    }
}
