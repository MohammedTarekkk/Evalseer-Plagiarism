<?php

namespace App\Http\Controllers;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Auth\Events\Registered;
use App\Models\User;
use Spatie\Permission\Models\Role;

class UserController extends Controller
{
    public function createUser(Request $request)
    {
        $request->validate([
            'name' => 'required|string|min:6|max:255',
            'username' => 'required|string|max:255|unique:users',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|min:6',
        ]);

        $user = new User();
        $user->name = $request->name;
        $user->username = $request->username;
        $user->email = $request->email;
        $user->password = bcrypt($request['password']);
        $user->save();

        Auth::login($user);
        $request->session()->regenerate();

        event(new Registered($user));

        return redirect()->route('home');
    }

    public function login(Request $request)
    {
        $credentials  = $request->only(['email','password']);
        if (Auth::attempt($credentials)) {
            $request->session()->regenerate();
            return redirect()->route('home');
        }
        return back()->withInput()->with('status','Invalid login details!');
    }

    //User Views START
    public function dashboard_users($users=null,$title="User"){
        $users = $users ?? User::paginate(15);
        return view('admin.users',['data_name'=>$title,'users'=>$users]);
    }

    public function dashboard_view_students(){
        $users = User::role('student')->paginate(15);
        return $this->dashboard_users($users,"Student");
    }

    public function dashboard_view_instructors(){
        $users = User::role('instructor')->paginate(15);
        return $this->dashboard_users($users, "Instructor");
    }
    //User Views END

    //User Add START
    public function add()
    {
        $roles = Role::all();
        return view('admin.add-user',['roles'=>$roles]);
    }
    public function store(Request $request)
    {
        $request->validate([
            'name'=>'required|string',
            'username'=>"required|string",
            'email'=>"required|email|unique:users,email",
            'birth_date'=>"nullable|date",
            'title'=>'nullable|string',
            'university_id'=>'nullable|string',
            'image' => "nullable|mimes:jpg,jpeg,png|max:1024",
            'phone' => "nullable|string",
            'password'=>"required|confirmed|string|min:6",
            'role'=>"required|array|min:1",
            'role.*'=>"required|string|exists:roles,name",
        ]);
        $user = new User();
        $user->name = $request->name;
        $user->username = $request->username;
        $user->email = $request->email;
        $user->birth_date = $request->birth_date;
        $user->title = $request->title;
        $user->university_id = $request->university_id;
        $user->phone = $request->phone;
        $user->password = bcrypt($request->password);
        if ($request->hasFile('image')) {
            $filenameWithExt = $request->file('image')->getClientOriginalName();
            $filename = pathinfo($filenameWithExt, PATHINFO_FILENAME);
            $extension = $request->file('image')->getClientOriginalExtension();
            $fileNameToStore = $request->name . '-' . time() . '.' . $extension;
            $path = $request->file('image')->storeAs('public/file', $fileNameToStore);
            $user->image = $fileNameToStore;
        }
        $user->save();
        foreach ($request->role as $role) {
            $user->assignRole($role);
        }
        return redirect()->back()->with('success','User created successfully!');
    }
    //User Add END
}