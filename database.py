"""SQLite persistence helpers for PROM-ACU."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import pandas as pd


DB_PATH = Path(__file__).resolve().parent / "prom_acu.db"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Open a SQLite connection and always close it."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """Create the database tables and indexes when they do not exist."""
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dni TEXT NOT NULL UNIQUE,
                age INTEGER NOT NULL CHECK (age BETWEEN 0 AND 120),
                sex TEXT NOT NULL,
                phone TEXT,
                diagnosis TEXT NOT NULL,
                main_complaint TEXT NOT NULL,
                assigned_scale TEXT NOT NULL,
                clinical_category TEXT,
                clinical_subcategory TEXT,
                suggested_prom TEXT,
                patient_code TEXT,
                care_origin TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                session_number INTEGER NOT NULL CHECK (session_number > 0),
                date TEXT NOT NULL,
                eva_pre REAL NOT NULL CHECK (eva_pre BETWEEN 0 AND 10),
                eva_post REAL NOT NULL CHECK (eva_post BETWEEN 0 AND 10),
                pgic INTEGER CHECK (pgic BETWEEN 1 AND 7),
                functional_impact REAL CHECK (
                    functional_impact BETWEEN 0 AND 10
                ),
                medication_name TEXT,
                medication_frequency TEXT,
                analgesic_change TEXT,
                adverse_event_severity TEXT,
                analgesic_use INTEGER NOT NULL DEFAULT 0,
                adverse_event INTEGER NOT NULL DEFAULT 0,
                adverse_event_description TEXT,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                UNIQUE (patient_id, session_number)
            );

            CREATE TABLE IF NOT EXISTS womac_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                assessment_type TEXT NOT NULL CHECK (
                    assessment_type IN ('Basal', 'Seguimiento', 'Final')
                ),
                session_number INTEGER NOT NULL CHECK (session_number > 0),
                pain_score INTEGER NOT NULL CHECK (pain_score BETWEEN 0 AND 20),
                stiffness_score INTEGER NOT NULL CHECK (
                    stiffness_score BETWEEN 0 AND 8
                ),
                function_score INTEGER NOT NULL CHECK (
                    function_score BETWEEN 0 AND 68
                ),
                total_score INTEGER NOT NULL CHECK (
                    total_score BETWEEN 0 AND 96
                ),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                UNIQUE (patient_id, session_number)
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_patient
            ON sessions(patient_id);

            CREATE INDEX IF NOT EXISTS idx_sessions_patient_date
            ON sessions(patient_id, date);

            CREATE INDEX IF NOT EXISTS idx_womac_patient
            ON womac_assessments(patient_id);
            """
        )

        session_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(sessions)").fetchall()
        }
        if "pgic" not in session_columns:
            connection.execute(
                "ALTER TABLE sessions ADD COLUMN pgic INTEGER "
                "CHECK (pgic BETWEEN 1 AND 7)"
            )
        if "functional_impact" not in session_columns:
            connection.execute(
                "ALTER TABLE sessions ADD COLUMN functional_impact REAL "
                "CHECK (functional_impact BETWEEN 0 AND 10)"
            )
        for column_name in (
            "medication_name",
            "medication_frequency",
            "analgesic_change",
            "adverse_event_severity",
        ):
            if column_name not in session_columns:
                connection.execute(
                    f"ALTER TABLE sessions ADD COLUMN {column_name} TEXT"
                )

        connection.execute(
            """
            UPDATE sessions
            SET adverse_event_severity = CASE
                WHEN adverse_event = 0 THEN 'Ninguno'
                WHEN adverse_event = 1 THEN 'No clasificado (histórico)'
            END
            WHERE adverse_event_severity IS NULL
            """
        )

        patient_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(patients)").fetchall()
        }
        for column_name in (
            "clinical_category",
            "clinical_subcategory",
            "suggested_prom",
            "patient_code",
            "care_origin",
        ):
            if column_name not in patient_columns:
                connection.execute(
                    f"ALTER TABLE patients ADD COLUMN {column_name} TEXT"
                )

        patients_without_code = connection.execute(
            "SELECT id FROM patients WHERE patient_code IS NULL "
            "OR TRIM(patient_code) = '' ORDER BY id"
        ).fetchall()
        for row in patients_without_code:
            connection.execute(
                "UPDATE patients SET patient_code = ? WHERE id = ?",
                (f"PAC-{int(row['id']):06d}", int(row["id"])),
            )

        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_patients_patient_code "
            "ON patients(patient_code)"
        )

        legacy_mappings = {
            "Rodilla": ("Musculoesquelético", "Rodilla", "WOMAC / KOOS"),
            "Cadera": ("Musculoesquelético", "Cadera", "WOMAC"),
            "Lumbalgia": ("Musculoesquelético", "Lumbar", "ODI"),
            "Cervicalgia": ("Musculoesquelético", "Cervical", "NDI"),
            "Hombro": ("Musculoesquelético", "Hombro", "SPADI"),
            "Insomnio": ("Salud mental y sueño", "Insomnio", "ISI"),
        }
        for legacy_complaint, classification in legacy_mappings.items():
            connection.execute(
                """
                UPDATE patients
                SET clinical_category = ?,
                    clinical_subcategory = ?,
                    suggested_prom = ?
                WHERE main_complaint = ?
                  AND clinical_category IS NULL
                  AND clinical_subcategory IS NULL
                  AND suggested_prom IS NULL
                """,
                (*classification, legacy_complaint),
            )

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS prom_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                score_min REAL,
                score_max REAL,
                score_direction TEXT NOT NULL CHECK (
                    score_direction IN (
                        'higher_is_worse',
                        'higher_is_better',
                        'not_applicable'
                    )
                ),
                implementation_status TEXT NOT NULL CHECK (
                    implementation_status IN ('implemented', 'planned')
                ),
                version TEXT,
                module_key TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS prom_indications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clinical_category TEXT NOT NULL,
                clinical_subcategory TEXT NOT NULL,
                instrument_id INTEGER NOT NULL,
                recommendation_role TEXT NOT NULL CHECK (
                    recommendation_role IN ('primary', 'alternative')
                ),
                priority INTEGER NOT NULL DEFAULT 1 CHECK (priority > 0),
                clinical_note TEXT,
                is_active INTEGER NOT NULL DEFAULT 1 CHECK (
                    is_active IN (0, 1)
                ),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instrument_id)
                    REFERENCES prom_catalog(id) ON DELETE RESTRICT,
                UNIQUE (
                    clinical_category,
                    clinical_subcategory,
                    instrument_id
                )
            );

            CREATE TABLE IF NOT EXISTS patient_prom_assignment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                instrument_id INTEGER NOT NULL,
                assignment_role TEXT NOT NULL CHECK (
                    assignment_role IN ('active', 'previous')
                ),
                selection_source TEXT NOT NULL CHECK (
                    selection_source IN (
                        'suggestion_accepted',
                        'alternative',
                        'manual',
                        'historical_womac'
                    )
                ),
                clinical_reason TEXT,
                assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                ended_at TEXT,
                is_active INTEGER NOT NULL DEFAULT 1 CHECK (
                    is_active IN (0, 1)
                ),
                FOREIGN KEY (patient_id)
                    REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (instrument_id)
                    REFERENCES prom_catalog(id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS prom_assessment_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                instrument_id INTEGER NOT NULL,
                assignment_id INTEGER,
                assessment_type TEXT NOT NULL,
                session_number INTEGER NOT NULL CHECK (session_number > 0),
                total_score REAL NOT NULL,
                normalized_score REAL,
                source_table TEXT NOT NULL,
                source_record_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (patient_id)
                    REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (instrument_id)
                    REFERENCES prom_catalog(id) ON DELETE RESTRICT,
                FOREIGN KEY (assignment_id)
                    REFERENCES patient_prom_assignment(id) ON DELETE SET NULL,
                UNIQUE (source_table, source_record_id)
            );

            CREATE INDEX IF NOT EXISTS idx_prom_indications_classification
            ON prom_indications(
                clinical_category,
                clinical_subcategory,
                is_active
            );

            CREATE INDEX IF NOT EXISTS idx_prom_assignment_patient
            ON patient_prom_assignment(patient_id, is_active);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_prom_one_active_per_patient
            ON patient_prom_assignment(patient_id)
            WHERE is_active = 1;

            CREATE INDEX IF NOT EXISTS idx_prom_assessment_patient
            ON prom_assessment_index(
                patient_id,
                instrument_id,
                session_number
            );
            """
        )

        catalog_seed = (
            (
                "WOMAC",
                "Western Ontario and McMaster Universities "
                "Osteoarthritis Index",
                "Dolor, rigidez y función física en artrosis de rodilla "
                "y cadera.",
                0,
                96,
                "higher_is_worse",
                "implemented",
                "Likert 0-4 resumido",
                "womac",
            ),
            (
                "KOOS",
                "Knee injury and Osteoarthritis Outcome Score",
                "Síntomas, función y calidad de vida relacionada con rodilla.",
                0,
                100,
                "higher_is_better",
                "planned",
                None,
                None,
            ),
            (
                "DASH",
                "Disabilities of the Arm, Shoulder and Hand",
                "Discapacidad y síntomas del miembro superior.",
                0,
                100,
                "higher_is_worse",
                "planned",
                None,
                None,
            ),
            (
                "ODI",
                "Oswestry Disability Index",
                "Discapacidad funcional relacionada con dolor lumbar.",
                0,
                100,
                "higher_is_worse",
                "planned",
                None,
                None,
            ),
            (
                "NDI",
                "Neck Disability Index",
                "Discapacidad relacionada con dolor cervical.",
                0,
                50,
                "higher_is_worse",
                "planned",
                None,
                None,
            ),
            (
                "HIT-6",
                "Headache Impact Test",
                "Impacto funcional de las cefaleas.",
                36,
                78,
                "higher_is_worse",
                "planned",
                None,
                None,
            ),
            (
                "SPADI",
                "Shoulder Pain and Disability Index",
                "Dolor y discapacidad específicos del hombro.",
                0,
                100,
                "higher_is_worse",
                "planned",
                None,
                None,
            ),
            (
                "RMDQ",
                "Roland-Morris Disability Questionnaire",
                "Limitación funcional relacionada con dolor lumbar.",
                0,
                24,
                "higher_is_worse",
                "planned",
                None,
                None,
            ),
            (
                "NPQ",
                "Northwick Park Neck Pain Questionnaire",
                "Dolor y discapacidad cervical.",
                0,
                100,
                "higher_is_worse",
                "planned",
                None,
                None,
            ),
            (
                "MIDAS",
                "Migraine Disability Assessment",
                "Discapacidad asociada con migraña y cefalea.",
                0,
                None,
                "higher_is_worse",
                "planned",
                None,
                None,
            ),
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO prom_catalog (
                code, name, description, score_min, score_max,
                score_direction, implementation_status, version, module_key
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            catalog_seed,
        )

        indication_seed = (
            (
                "Musculoesquelético",
                "Rodilla",
                "WOMAC",
                "primary",
                1,
                "Seguimiento de dolor, rigidez y función en rodilla.",
            ),
            (
                "Musculoesquelético",
                "Rodilla",
                "KOOS",
                "alternative",
                1,
                "Alternativa específica para lesión y artrosis de rodilla.",
            ),
            (
                "Musculoesquelético",
                "Hombro",
                "DASH",
                "primary",
                1,
                "Seguimiento funcional del miembro superior.",
            ),
            (
                "Musculoesquelético",
                "Hombro",
                "SPADI",
                "alternative",
                1,
                "Alternativa específica para dolor y discapacidad de hombro.",
            ),
            (
                "Musculoesquelético",
                "Lumbar",
                "ODI",
                "primary",
                1,
                "Seguimiento de discapacidad por dolor lumbar.",
            ),
            (
                "Musculoesquelético",
                "Lumbar",
                "RMDQ",
                "alternative",
                1,
                "Alternativa funcional para dolor lumbar.",
            ),
            (
                "Musculoesquelético",
                "Cervical",
                "NDI",
                "primary",
                1,
                "Seguimiento de discapacidad cervical.",
            ),
            (
                "Musculoesquelético",
                "Cervical",
                "NPQ",
                "alternative",
                1,
                "Alternativa para dolor y discapacidad cervical.",
            ),
            (
                "Cefaleas",
                "Cefalea",
                "HIT-6",
                "primary",
                1,
                "Seguimiento del impacto funcional de la cefalea.",
            ),
            (
                "Cefaleas",
                "Cefalea",
                "MIDAS",
                "alternative",
                1,
                "Alternativa para discapacidad asociada con cefalea.",
            ),
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO prom_indications (
                clinical_category, clinical_subcategory, instrument_id,
                recommendation_role, priority, clinical_note
            )
            SELECT ?, ?, id, ?, ?, ?
            FROM prom_catalog
            WHERE code = ?
            """,
            (
                (category, subcategory, role, priority, note, code)
                for (
                    category,
                    subcategory,
                    code,
                    role,
                    priority,
                    note,
                ) in indication_seed
            ),
        )

        connection.execute(
            """
            INSERT INTO patient_prom_assignment (
                patient_id,
                instrument_id,
                assignment_role,
                selection_source,
                clinical_reason,
                assigned_at,
                is_active
            )
            SELECT DISTINCT
                w.patient_id,
                c.id,
                'active',
                'historical_womac',
                'Asignación inicial basada en una evaluación WOMAC existente.',
                MIN(w.created_at),
                1
            FROM womac_assessments w
            JOIN prom_catalog c ON c.code = 'WOMAC'
            WHERE NOT EXISTS (
                SELECT 1
                FROM patient_prom_assignment a
                WHERE a.patient_id = w.patient_id
                  AND a.is_active = 1
            )
            GROUP BY w.patient_id, c.id
            """
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO prom_assessment_index (
                patient_id,
                instrument_id,
                assignment_id,
                assessment_type,
                session_number,
                total_score,
                normalized_score,
                source_table,
                source_record_id,
                created_at
            )
            SELECT
                w.patient_id,
                c.id,
                a.id,
                w.assessment_type,
                w.session_number,
                w.total_score,
                ROUND((w.total_score * 100.0) / 96.0, 2),
                'womac_assessments',
                w.id,
                w.created_at
            FROM womac_assessments w
            JOIN prom_catalog c ON c.code = 'WOMAC'
            LEFT JOIN patient_prom_assignment a
                ON a.patient_id = w.patient_id
                AND a.instrument_id = c.id
                AND a.is_active = 1
            """
        )


def add_patient(
    name: str,
    dni: str,
    age: int,
    sex: str,
    phone: str,
    diagnosis: str,
    main_complaint: str,
    assigned_scale: str,
    clinical_category: str,
    clinical_subcategory: str,
    suggested_prom: str,
    care_origin: str,
) -> int:
    """Insert a patient and return the generated identifier."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO patients (
                name, dni, age, sex, phone, diagnosis,
                main_complaint, assigned_scale, clinical_category,
                clinical_subcategory, suggested_prom, care_origin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name.strip(),
                dni.strip(),
                age,
                sex,
                phone.strip(),
                diagnosis.strip(),
                main_complaint,
                assigned_scale,
                clinical_category,
                clinical_subcategory,
                suggested_prom,
                care_origin,
            ),
        )
        patient_id = int(cursor.lastrowid)
        connection.execute(
            "UPDATE patients SET patient_code = ? WHERE id = ?",
            (f"PAC-{patient_id:06d}", patient_id),
        )
        return patient_id


def add_session(
    patient_id: int,
    session_number: int,
    date: str,
    eva_pre: float,
    eva_post: float,
    pgic: int,
    functional_impact: float,
    medication_name: str,
    medication_frequency: str,
    analgesic_change: str,
    adverse_event_severity: str,
    adverse_event_description: str,
    notes: str,
) -> int:
    """Insert a clinical session and return its identifier."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO sessions (
                patient_id, session_number, date, eva_pre, eva_post, pgic,
                functional_impact, medication_name, medication_frequency,
                analgesic_change, adverse_event_severity,
                analgesic_use, adverse_event, adverse_event_description, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                session_number,
                date,
                eva_pre,
                eva_post,
                pgic,
                functional_impact,
                medication_name.strip(),
                medication_frequency.strip(),
                analgesic_change,
                adverse_event_severity,
                int(analgesic_change != "No usa"),
                int(adverse_event_severity != "Ninguno"),
                adverse_event_description.strip(),
                notes.strip(),
            ),
        )
        return int(cursor.lastrowid)


def get_patients() -> pd.DataFrame:
    """Return all patients ordered by name."""
    with get_connection() as connection:
        return pd.read_sql_query(
            "SELECT * FROM patients ORDER BY name COLLATE NOCASE",
            connection,
        )


def get_patient(patient_id: int) -> dict[str, Any] | None:
    """Return one patient as a dictionary."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM patients WHERE id = ?",
            (patient_id,),
        ).fetchone()
        return dict(row) if row else None


def get_patient_sessions(patient_id: int) -> pd.DataFrame:
    """Return a patient's sessions in clinical order."""
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT *
            FROM sessions
            WHERE patient_id = ?
            ORDER BY session_number ASC, date ASC, id ASC
            """,
            connection,
            params=(patient_id,),
        )


def add_womac_assessment(
    patient_id: int,
    assessment_type: str,
    session_number: int,
    pain_score: int,
    stiffness_score: int,
    function_score: int,
) -> int:
    """Insert a summarized WOMAC Likert assessment."""
    total_score = pain_score + stiffness_score + function_score
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO womac_assessments (
                patient_id, assessment_type, session_number,
                pain_score, stiffness_score, function_score, total_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                assessment_type,
                session_number,
                pain_score,
                stiffness_score,
                function_score,
                total_score,
            ),
        )
        return int(cursor.lastrowid)


def get_patient_womac_assessments(patient_id: int) -> pd.DataFrame:
    """Return a patient's WOMAC assessments in follow-up order."""
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT *
            FROM womac_assessments
            WHERE patient_id = ?
            ORDER BY session_number ASC, id ASC
            """,
            connection,
            params=(patient_id,),
        )


def get_womac_dashboard_assessments() -> pd.DataFrame:
    """Return pseudonymized WOMAC records for dashboard calculations."""
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT
                w.id,
                w.patient_id,
                p.patient_code,
                p.diagnosis,
                p.clinical_category,
                p.clinical_subcategory,
                p.care_origin,
                w.assessment_type,
                w.session_number,
                w.total_score,
                w.created_at
            FROM womac_assessments w
            JOIN patients p ON p.id = w.patient_id
            ORDER BY
                p.patient_code,
                w.session_number,
                w.id
            """,
            connection,
        )


def womac_assessment_exists(patient_id: int, session_number: int) -> bool:
    """Check whether WOMAC is already recorded for a session."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM womac_assessments
            WHERE patient_id = ? AND session_number = ?
            LIMIT 1
            """,
            (patient_id, session_number),
        ).fetchone()
        return row is not None


def get_dashboard_data() -> pd.DataFrame:
    """Return patient and session data needed by the medical dashboard."""
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT
                p.id,
                p.name,
                p.dni,
                p.phone,
                p.patient_code,
                p.diagnosis,
                p.main_complaint,
                p.assigned_scale,
                p.clinical_category,
                p.clinical_subcategory,
                p.suggested_prom,
                p.care_origin,
                (
                    SELECT s.eva_pre
                    FROM sessions s
                    WHERE s.patient_id = p.id
                    ORDER BY s.session_number ASC, s.date ASC, s.id ASC
                    LIMIT 1
                ) AS baseline_eva,
                (
                    SELECT s.eva_pre
                    FROM sessions s
                    WHERE s.patient_id = p.id
                    ORDER BY s.session_number DESC, s.date DESC, s.id DESC
                    LIMIT 1
                ) AS latest_eva,
                (
                    SELECT s.pgic
                    FROM sessions s
                    WHERE s.patient_id = p.id
                    ORDER BY s.session_number DESC, s.date DESC, s.id DESC
                    LIMIT 1
                ) AS latest_pgic,
                (
                    SELECT s.functional_impact
                    FROM sessions s
                    WHERE s.patient_id = p.id
                    ORDER BY s.session_number DESC, s.date DESC, s.id DESC
                    LIMIT 1
                ) AS latest_functional_impact,
                (
                    SELECT s.analgesic_change
                    FROM sessions s
                    WHERE s.patient_id = p.id
                    ORDER BY s.session_number DESC, s.date DESC, s.id DESC
                    LIMIT 1
                ) AS latest_analgesic_change,
                (
                    SELECT s.adverse_event_severity
                    FROM sessions s
                    WHERE s.patient_id = p.id
                    ORDER BY s.session_number DESC, s.date DESC, s.id DESC
                    LIMIT 1
                ) AS latest_adverse_event_severity,
                EXISTS (
                    SELECT 1
                    FROM sessions s
                    WHERE s.patient_id = p.id
                      AND COALESCE(s.adverse_event_severity, 'Ninguno')
                          != 'Ninguno'
                ) AS has_adverse_event,
                (
                    SELECT w.total_score
                    FROM womac_assessments w
                    WHERE w.patient_id = p.id
                      AND w.assessment_type = 'Basal'
                    ORDER BY w.session_number ASC, w.id ASC
                    LIMIT 1
                ) AS baseline_womac,
                (
                    SELECT w.total_score
                    FROM womac_assessments w
                    WHERE w.patient_id = p.id
                    ORDER BY w.session_number DESC, w.id DESC
                    LIMIT 1
                ) AS latest_womac,
                COUNT(s2.id) AS session_count
            FROM patients p
            LEFT JOIN sessions s2 ON s2.patient_id = p.id
            GROUP BY p.id
            ORDER BY p.name COLLATE NOCASE
            """,
            connection,
        )


def get_pseudonymized_research_data() -> pd.DataFrame:
    """Return session-level research data without direct identifiers."""
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            WITH patient_events AS (
                SELECT patient_id, session_number
                FROM sessions
                UNION
                SELECT patient_id, session_number
                FROM womac_assessments
            )
            SELECT
                p.patient_code,
                p.age,
                p.sex,
                p.diagnosis,
                p.clinical_category,
                p.clinical_subcategory,
                p.suggested_prom,
                COALESCE(
                    p.care_origin,
                    'Pendiente de clasificación'
                ) AS origen_asistencial,
                s.session_number,
                s.eva_pre,
                s.eva_post,
                s.pgic,
                s.functional_impact,
                s.medication_name,
                s.medication_frequency,
                s.analgesic_change,
                s.adverse_event_severity,
                s.adverse_event,
                w.assessment_type AS womac_assessment_type,
                w.session_number AS womac_session_number,
                w.pain_score AS womac_pain_score,
                w.stiffness_score AS womac_stiffness_score,
                w.function_score AS womac_function_score,
                w.total_score AS womac_total_score
            FROM patients p
            LEFT JOIN patient_events e ON e.patient_id = p.id
            LEFT JOIN sessions s
                ON s.patient_id = e.patient_id
                AND s.session_number = e.session_number
            LEFT JOIN womac_assessments w
                ON w.patient_id = e.patient_id
                AND w.session_number = e.session_number
            ORDER BY
                p.patient_code,
                e.session_number,
                s.date,
                s.id,
                w.id
            """,
            connection,
        )


def dni_exists(dni: str) -> bool:
    """Check whether a DNI is already registered."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT 1 FROM patients WHERE dni = ? LIMIT 1",
            (dni.strip(),),
        ).fetchone()
        return row is not None


def session_number_exists(patient_id: int, session_number: int) -> bool:
    """Check whether a session number is already in use for a patient."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM sessions
            WHERE patient_id = ? AND session_number = ?
            LIMIT 1
            """,
            (patient_id, session_number),
        ).fetchone()
        return row is not None
