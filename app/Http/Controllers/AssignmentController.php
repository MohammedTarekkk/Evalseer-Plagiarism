<?php

namespace App\Http\Controllers;

use App\Models\Assignments;
use App\Models\Course;
use Illuminate\Http\Request;

class AssignmentController extends Controller
{
    public function add(){
        $courses = Course::all();
        return view('instructor.add-assignment',['courses'=>$courses]);
    }

    public function store(Request $request){
        $request->validate([
            'name'=>'required|string',
            'description' => 'nullable|string',
            'start_time'=> "required|date",
            'end_time' => "required|date",
            'late_time' => "required|date",
            'max' => "required|numeric",
            'grade' => "required|numeric",
            'pdf' => "nullable|mimes:pdf",
            'course_id' => "required|exists:courses,id",
            'group_id' => "nullable|exists:groups,id",
        ]);
        $assignment = new Assignments();
        $assignment->name = $request->name;
        if($request->has('description'))
            $assignment->description = $request->description;
        
        $assignment->start_time = $request->start_time;
        $assignment->end_time = $request->end_time;
        $assignment->late_time = $request->late_time;
        $assignment->submissions = $request->max;
        $assignment->grade = $request->grade;
        $assignment->course_id = $request->course_id;
        if($request->has('group_id'))
            $assignment->group_id = $request->group_id;
        if($request->hasFile('pdf')){
            $filenameWithExt = $request->file('pdf')->getClientOriginalName();
            $filename = pathinfo($filenameWithExt, PATHINFO_FILENAME);
            $extension = $request->file('pdf')->getClientOriginalExtension();
            $fileNameToStore = $request->name . '-' . time() . '.' . $extension;
            $path = $request->file('pdf')->storeAs('public/file', $fileNameToStore);
            $assignment->pdf = $fileNameToStore;
        }
        $assignment->save();
        return redirect()->route('dashboard.add_question',$assignment->id);
    }

    public function view($id){
        $assignment = Assignments::with('questions.test_cases')->find($id);
        return view('submission',["assignment"=>$assignment]);
    }

    public function submit_assignment(Request $request){
        $request->validate([
            "submission.*"=>"required|array",
        ]);
    }
    
}