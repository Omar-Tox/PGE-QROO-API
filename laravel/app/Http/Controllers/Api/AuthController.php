<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use App\Models\User;
use Illuminate\Validation\ValidationException;

class AuthController extends Controller
{
    /**
     * handle the login request
     */
    public function login (Request $request) {
        $request->validate([
            'email' => 'required|email',
            'contrasena' => 'required'
        ]);

        //Search the user's email
        $user = User::where('email', $request->email)->first();

        //Verify the user and password
        if(!$user || !Hash::check($request->contrasena, $user->contrasena)) {
            throw ValidationException::withMessages([
                'email' => ['Credenciales proporcionadas incorrectas']
            ]);
        }

        //Verify if the user is active
        if(!$user->activo) {
            throw ValidationException::withMessages([
                'email' => ['Sesión expirada ó desactivada']
            ]);
        }

        //Update user's last login
        $user->ultimo_login = now();
        $user->save();

        //Create the token
        $token = $user->createToken('auth_token')->plainTextToken;

        return response()->json([
            'message' => 'login exitoso',
            'acces_token' => $token,
            'token_type' => 'Bearer',
            'user' => [
                'id' => $user->id_usuario,
                'nombre' => $user->nombre,
                'nombre_usuario' => $user->nombre_usuario,
                'email' => $user->email,
            ]
        ]);
    }

    /**
     * Handle a auth response
     */
    public function me (Request $request) {

        $user = $request->user(); // El middleware 'auth:sanctum' ya nos da el $request->user()

        //Load the relations between roles/dependencias
        $user->load('roles', 'dependencias');
        
        return response()->json($user);
    }

    /**
     * Logout function
     */

    public function logout (Request $request) {
        $request->user()->currentAccessToken()->Delete();

        return response()->json([
            'message' => 'Sesión cerrada correctamente'
        ]);
    }
}
