
-- =============================================================
-- SECTORES
-- =============================================================
INSERT INTO sector (nombre_sector, descripcion) VALUES
('Educación', 'Instituciones educativas del estado'),
('Salud', 'Instituciones del sector salud'),
('Energía y Medio Ambiente', 'Dependencias relacionadas con energía y medio ambiente'),
('Infraestructura', 'Obras públicas e infraestructura gubernamental'),
('Finanzas y Administración', 'Gestión financiera del gobierno estatal');

-- =============================================================
-- DEPENDENCIAS
-- =============================================================
INSERT INTO dependencias (nombre_dependencia, id_sector) VALUES
('Secretaría de Educación de Quintana Roo (SEQ)', 1),
('Universidad de Quintana Roo (UQROO)', 1),
('Secretaría de Salud de Quintana Roo (SESA)', 2),
('Comisión de Agua Potable y Alcantarillado (CAPA)', 3),
('Secretaría de Obras Públicas (SEOP)', 4),
('Secretaría de Finanzas y Planeación (SEFIPLAN)', 5),
('Colegio de Bachilleres del Estado de Q. Roo (COBAQROO)', 1),
('Secretaría de Medio Ambiente (SEMA)', 3),
('Instituto de Infraestructura Física Educativa (IFEQROO)', 4),
('Servicios Estatales de Salud Mental (SESA-Mental)', 2);

-- =============================================================
-- EDIFICIOS
-- =============================================================
INSERT INTO edificio (id_dependencia, nombre_edificio, direccion, latitud, longitud, caracteristicas) VALUES
(1, 'Edificio Central SEQ', 'Av. Insurgentes 123, Chetumal, Q. Roo', 18.500000, -88.300000, 'Oficinas administrativas principales'),
(2, 'Campus Chetumal UQROO', 'Blvd. Bahía s/n, Chetumal, Q. Roo', 18.505000, -88.285000, 'Campus universitario principal'),
(3, 'Hospital General de Chetumal', 'Av. Independencia 456, Chetumal', 18.510000, -88.290000, 'Hospital regional con alta demanda'),
(4, 'Planta de Tratamiento CAPA', 'Carretera Calderitas km 5', 18.520000, -88.270000, 'Instalación técnica de tratamiento de agua'),
(5, 'Centro de Operaciones SEOP', 'Av. Universidad 789, Chetumal', 18.508000, -88.295000, 'Base de maquinaria e ingenieros civiles'),
(6, 'Oficinas Centrales SEFIPLAN', 'Blvd. Bahía 230, Chetumal, Q. Roo', 18.497000, -88.302000, 'Centro financiero del estado'),
(7, 'COBAQROO Plantel 1', 'Av. Maxuxac 410, Chetumal', 18.511000, -88.298000, 'Institución de educación media superior'),
(8, 'Edificio Ambiental SEMA', 'Col. Centro, Chetumal', 18.503000, -88.294000, 'Oficinas ambientales del gobierno estatal'),
(9, 'Oficinas IFEQROO', 'Av. Álvaro Obregón 612, Chetumal', 18.507000, -88.291000, 'Dirección de infraestructura escolar'),
(10, 'Centro de Salud Mental SESA', 'Av. Erick Paolo Martínez 789, Chetumal', 18.512000, -88.287000, 'Unidad especializada en salud mental');

-- =============================================================
-- PRESUPUESTOS (2015 - 2025)
-- =============================================================
DO $$
DECLARE
    dep_id INT;
    anio INT;
    trim INT;
BEGIN
    FOR dep_id IN 1..10 LOOP
        FOR anio IN 2015..2024 LOOP
            FOR trim IN 1..4 LOOP
                INSERT INTO presupuestos (id_dependencia, anio, trimestre, monto_asignado)
                VALUES (dep_id, anio, trim, ROUND((RANDOM() * 7000000 + 1500000)::NUMERIC, 2));
            END LOOP;
        END LOOP;
    END LOOP;
END $$;

-- =============================================================
-- CONSUMO HISTÓRICO (2015 - 2025)
-- =============================================================
DO $$
DECLARE
    edif_id INT;
    anio INT;
    mes INT;
    consumo NUMERIC;
BEGIN
    FOR edif_id IN 1..10 LOOP
        FOR anio IN 2015..2025 LOOP
            FOR mes IN 1..12 LOOP
                consumo := ROUND((RANDOM() * 35000 + 3000)::NUMERIC, 2);
                INSERT INTO consumo_historico (id_edificio, anio, mes, consumo_kwh, costo_total, fuente_dato)
                VALUES (edif_id, anio, mes, consumo, ROUND(consumo * (RANDOM() * 1.8 + 0.8)::NUMERIC, 2), 'CFE');
            END LOOP;
        END LOOP;
    END LOOP;
END $$;
