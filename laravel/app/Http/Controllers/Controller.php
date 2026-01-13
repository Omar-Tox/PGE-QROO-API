<?php

namespace App\Http\Controllers;
/**
 * @OA\Info(
 *     version="1.0.0",
 *     title="API PGE-QROO",
 *     description="Documentación de la API para la Plataforma de Gestión Energética de Quintana Roo. Permite la gestión de dependencias, edificios, presupuestos y análisis de consumo."
 * )
 *
 * @OA\SecurityScheme(
 *     securityScheme="sanctum",
 *     type="http",
 *     scheme="bearer"
 * )
 *
 * @OA\Schema(
 *     schema="UserAuthResponse",
 *     title="Usuario Autenticado (Respuesta Login)",
 *     type="object",
 *     @OA\Property(property="id", type="integer", example=5),
 *     @OA\Property(property="nombre", type="string", example="Juan Pérez"),
 *     @OA\Property(property="nombre_usuario", type="string", example="jperez"),
 *     @OA\Property(property="email", type="string", format="email", example="juan.perez@ejemplo.com")
 * )
 * 
 * * @OA\Schema(
 *     schema="RankingConsumoDependencia",
 *     title="Ranking de Consumo por Dependencia",
 *     description="Datos agregados de consumo energético por dependencia",
 *     type="object",
 *     @OA\Property(property="id_dependencia", type="integer", example=1),
 *     @OA\Property(property="nombre_dependencia", type="string", example="Secretaría de Educación"),
 *     @OA\Property(property="total_consumo", type="number", format="float", example=15432.75),
 *     @OA\Property(property="total_costo", type="number", format="float", example=32145.50)
 * )

 * @OA\Schema(
 *     schema="ErrorCargaConsumo",
 *     title="Error en Carga Masiva de Consumos",
 *     description="Detalle de error detectado en una fila del archivo importado",
 *     type="object",
 *     @OA\Property(property="fila", type="integer", example=12),
 *     @OA\Property(property="columna", type="string", example="consumo_kwh"),
 *     @OA\Property(
 *         property="error",
 *         type="array",
 *         @OA\Items(type="string", example="El consumo debe ser numérico")
 *     ),
 *     @OA\Property(property="valor_erroneo", type="string", example="ABC123")
 * ) 
 *
 * @OA\Schema(
 *     schema="UserFullResponse",
 *     title="Usuario Completo (Endpoint /me)",
 *     allOf={
 *         @OA\Schema(ref="#/components/schemas/UserAuthResponse"),
 *         @OA\Schema(
 *             type="object",
 *             @OA\Property(property="activo", type="boolean", example=true),
 *             @OA\Property(
 *                 property="ultimo_login",
 *                 type="string",
 *                 format="date-time",
 *                 example="2025-12-13T05:00:00.000000Z"
 *             ),
 *             @OA\Property(
 *                 property="roles",
 *                 type="array",
 *                 @OA\Items(
 *                     type="object",
 *                     example={"id": 1, "name": "Administrador"}
 *                 )
 *             ),
 *             @OA\Property(
 *                 property="dependencias",
 *                 type="array",
 *                 @OA\Items(
 *                     type="object",
 *                     example={"id": 1, "name": "Secretaría A"}
 *                 )
 *             )
 *         )
 *     }
 * )
 * 
 * @OA\Schema(
 *     schema="EvolucionConsumo",
 *     title="Evolución de Consumo Energético",
 *     description="Consumo y costo energético por mes",
 *     type="object",
 *     @OA\Property(property="año", type="integer", example=2025),
 *     @OA\Property(property="mes", type="integer", example=6),
 *     @OA\Property(property="total_consumo", type="number", format="float", example=13250.75),
 *     @OA\Property(property="total_costo", type="number", format="float", example=28900.40)
 * )
 * 
 * @OA\Schema(
 *     schema="InmuebleTopConsumo",
 *     title="Inmueble con Mayor Consumo",
 *     description="Inmueble con mayor consumo energético en el periodo",
 *     type="object",
 *     @OA\Property(property="nombre_edificio", type="string", example="Edificio Central"),
 *     @OA\Property(property="consumo", type="number", format="float", example=5420.80)
 * )
 * 
 * @OA\Get(
 *     path="/api/integracion/gobierno",
 *     tags={"Integración"},
 *     summary="Obtener datos oficiales del Gobierno",
 *     description="Consulta el servicio externo Núcleo Digital.",
 *     security={{"sanctum":{}}},
 *
 *     @OA\Response(
 *         response=200,
 *         description="Datos obtenidos correctamente",
 *         @OA\JsonContent(type="object")
 *     ),
 *
 *     @OA\Response(
 *         response=502,
 *         description="Error al conectar con el Núcleo Digital"
 *     )
 * )
 * 
 * @OA\Schema(
 *     schema="Presupuesto",
 *     type="object",
 *     required={"año","trimestre","monto_asignado","dependencia_id"},
 *     @OA\Property(property="id", type="integer", example=1),
 *     @OA\Property(property="año", type="integer", example=2024),
 *     @OA\Property(property="trimestre", type="integer", example=1),
 *     @OA\Property(property="monto_asignado", type="number", format="float", example=150000.50),
 *     @OA\Property(property="dependencia_id", type="integer", example=3)
 * )
 * 
 * @OA\Schema(
 *     schema="Usuario",
 *     type="object",
 *     @OA\Property(property="id_usuario", type="integer", example=1),
 *     @OA\Property(property="nombre_usuario", type="string", example="admin"),
 *     @OA\Property(property="nombre", type="string", example="Juan"),
 *     @OA\Property(property="apellido", type="string", example="Pérez"),
 *     @OA\Property(property="email", type="string", format="email", example="admin@pgeqroo.com"),
 *     @OA\Property(property="activo", type="boolean", example=true),
 *     @OA\Property(
 *         property="roles",
 *         type="array",
 *         @OA\Items(type="object", example={"id":1,"nombre":"Administrador"})
 *     ),
 *     @OA\Property(
 *         property="dependencias",
 *         type="array",
 *         @OA\Items(type="object", example={"id":2,"nombre":"Secretaría A"})
 *     )
 * )
 *
 * @OA\Schema(
 *     schema="AsignacionRol",
 *     type="object",
 *     required={"rol_id","dependencia_id"},
 *     @OA\Property(property="rol_id", type="integer", example=1),
 *     @OA\Property(property="dependencia_id", type="integer", example=2)
 * )
 */
abstract class Controller
{
    //
}
