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
 * @OA\Post(
 *     path="/api/login",
 *     tags={"Autenticación"},
 *     summary="Iniciar sesión",
 *     description="Obtiene un token de acceso para el sistema.",
 *     @OA\RequestBody(
 *         required=true,
 *         @OA\JsonContent(
 *             required={"email","contrasena"},
 *             @OA\Property(property="email", type="string", format="email", example="admin@pgeqroo.com"),
 *             @OA\Property(property="contrasena", type="string", format="password", example="password123")
 *         )
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Login exitoso",
 *         @OA\JsonContent(
 *             @OA\Property(property="message", type="string", example="login exitoso"),
 *             @OA\Property(property="access_token", type="string", example="1|AbCdEf123..."),
 *             @OA\Property(property="token_type", type="string", example="Bearer"),
 *             @OA\Property(property="user", ref="#/components/schemas/UserAuthResponse")
 *         )
 *     ),
 *     @OA\Response(
 *         response=401,
 *         description="Credenciales incorrectas"
 *     ),
 *     @OA\Response(
 *         response=422,
 *         description="Datos inválidos"
 *     )
 * )
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
     * @OA\Get(
            * path="/api/me",
            * tags={"Autenticación"},
            * summary="Obtener usuario autenticado",
            * description="Devuelve los datos del usuario logueado. Requiere Bearer Token.",
            * security={{"sanctum": {}}},
     * @OA\Response(
            * response=200,
            * description="Datos del usuario recuperados",
     * @OA\JsonContent(ref="#/components/schemas/UserFullResponse")
     * ),
     * @OA\Response(response=401, description="No autenticado")
     * )
     */

    public function me (Request $request) {

        $user = $request->user(); // El middleware 'auth:sanctum' ya nos da el $request->user()

        //Load the relations between roles/dependencias
        $user->load('roles', 'dependencias');
        
        return response()->json($user);
    }

    /**
     * @OA\Post(
            * path="/api/logout",
            * tags={"Autenticación"},
            * summary="Cerrar sesión",
            * description="Elimina el token de acceso actual del usuario. Requiere Bearer Token.",
            * security={{"sanctum": {}}},
     * @OA\Response(
            * response=200,
            * description="Sesión cerrada correctamente",
     * @OA\JsonContent(
     * @OA\Property(property="message", type="string", example="Sesión cerrada correctamente")
     * )
     * ),
     *  
     * )
     */

    public function logout (Request $request) {
        $request->user()->currentAccessToken()->Delete();

        return response()->json([
            'message' => 'Sesión cerrada correctamente'
        ]);
    }
}
