"""PROM-ACU: simple clinical follow-up demo built with Streamlit."""

from __future__ import annotations

import importlib
import json
import sqlite3
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st
import database as database_module

from database import (
    add_patient,
    add_session,
    add_womac_assessment,
    dni_exists,
    get_dashboard_data,
    get_patient,
    get_patient_sessions,
    get_patient_womac_assessments,
    get_patients,
    get_pseudonymized_research_data,
    init_db,
    session_number_exists,
    womac_assessment_exists,
)
from utils import (
    ADVERSE_EVENT_SEVERITY_OPTIONS,
    ANALGESIC_CHANGE_OPTIONS,
    CLINICAL_CLASSIFICATION,
    MEDICAL_WARNING,
    PSEUDONYMIZATION_WARNING,
    PGIC_OPTIONS,
    build_clinical_report,
    clinical_status,
    enrich_dashboard_data,
    format_functional_impact,
    format_optional_text,
    format_pgic,
    get_prom_implementation_status,
    get_suggested_prom,
)

if not hasattr(database_module, "get_womac_dashboard_assessments"):
    database_module = importlib.reload(database_module)
get_womac_dashboard_assessments = (
    database_module.get_womac_dashboard_assessments
)


st.set_page_config(
    page_title="PROM-ACU",
    page_icon="🩺",
    layout="wide",
)


def show_medical_warning() -> None:
    """Display the mandatory medical disclaimer."""
    st.warning(MEDICAL_WARNING, icon="⚠️")


def hide_sidebar() -> None:
    """Hide Streamlit sidebar during the guided intake screens."""
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"],
            [data-testid="collapsedControl"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_step() -> None:
    """Show three accessible consultation choices as distinct cards."""
    hide_sidebar()
    st.markdown(
        """
        <style>
            div[data-testid="stVerticalBlockBorderWrapper"]
            div[data-testid="stButton"] button {
                min-height: 4rem;
                font-size: 1.3rem;
                font-weight: 700;
                line-height: 1.25;
                white-space: normal;
            }
            .welcome-card-help {
                font-size: 1.2rem;
                line-height: 1.55;
                color: #30343b;
                margin: 0.35rem 0 0.2rem 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("¡Bienvenida/o!")
    st.subheader("ACUPUNTURA NEUROBIOENERGÉTICA")
    st.write("Dr. Mauricio Uehara")
    st.write("¿Qué tipo de consulta desea realizar?")

    with st.container(border=True):
        if st.button(
            "Soy paciente nuevo",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["tipo_consulta"] = "Paciente nuevo"
            st.session_state["new_problem_existing_patient"] = False
            st.session_state["guided_step"] = "consent"
            st.rerun()
        st.markdown(
            '<p class="welcome-card-help">Primera vez que consulta con el '
            "Dr. Mauricio Uehara.</p>",
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        if st.button(
            "Estoy realizando tratamiento",
            use_container_width=True,
        ):
            st.session_state["tipo_consulta"] = "Seguimiento de tratamiento"
            st.session_state["guided_step"] = "followup_search"
            st.rerun()
        st.markdown(
            '<p class="welcome-card-help">Ya comenzó sus sesiones y desea '
            "informar cómo evolucionó desde la última consulta.</p>",
            unsafe_allow_html=True,
        )

    with st.container(border=True):
        if st.button(
            "Ya fui paciente y quiero una nueva consulta",
            use_container_width=True,
        ):
            st.session_state["tipo_consulta"] = (
                "Nueva consulta de paciente ya registrado"
            )
            st.session_state["new_problem_existing_patient"] = True
            st.session_state["guided_step"] = "returning_patient_search"
            st.rerun()
        st.markdown(
            '<p class="welcome-card-help">Fue atendido anteriormente y ahora '
            "desea consultar nuevamente, por recaída o por otra dolencia.</p>",
            unsafe_allow_html=True,
        )

    st.divider()
    if st.button("Panel profesional", type="tertiary"):
        st.session_state["guided_step"] = "professional_panel"
        st.rerun()

def render_back_button(previous_step: str) -> None:
    """Allow patients to return to the previous guided step without clearing data."""
    if st.button("Volver atrás", use_container_width=True):
        st.session_state["guided_step"] = previous_step
        st.rerun()


def option_index(options: list[str], selected: str | None) -> int | None:
    """Return the index for a previously selected option."""
    if selected in options:
        return options.index(selected)
    return None


def fix_visible_encoding(value):
    """Repair common UTF-8 mojibake only for text rendered on screen."""
    if not isinstance(value, str) or not any(marker in value for marker in ("Ã", "Â")):
        return value
    try:
        return value.encode("latin1").decode("utf-8")
    except UnicodeError:
        return value


def render_patient_navigation(
    previous_step: str,
    next_label: str = "Siguiente",
    *,
    on_back=None,
    on_next=None,
    next_step: str | None = None,
) -> None:
    """Render bottom navigation for patient guided-flow screens."""
    back_col, next_col = st.columns(2)
    with back_col:
        if st.button("Atrás", use_container_width=True):
            if on_back is not None:
                on_back()
            st.session_state["guided_step"] = previous_step
            st.rerun()
    with next_col:
        if st.button(next_label, type="primary", use_container_width=True):
            if on_next is not None and not on_next():
                return
            if next_step is not None:
                st.session_state["guided_step"] = next_step
            st.rerun()


def show_dictation_help() -> None:
    """Show a short mobile dictation hint below long text fields."""
    st.caption("Puede escribir o dictar desde el micrófono del celular.")


def render_informed_consent_step() -> None:
    """Show the informed consent before starting the guided intake."""
    hide_sidebar()
    st.title("Consentimiento informado")
    st.write(
        "Esta aplicación permite registrar información previa o complementaria "
        "a la consulta médica.\n\n"
        "Los datos serán utilizados por el Dr. Mauricio Uehara para orientar "
        "el seguimiento clínico.\n\n"
        "La aplicación puede utilizar asistencia por inteligencia artificial "
        "para organizar la información ingresada, pero no reemplaza la "
        "evaluación médica presencial, no emite diagnósticos automáticos y "
        "no indica tratamientos por sí sola.\n\n"
        "Los datos personales serán tratados de manera confidencial. Para "
        "análisis, informes o exportaciones, la información clínica deberá "
        "utilizarse en forma seudonimizada o anonimizada, evitando identificar "
        "directamente al paciente."
    )
    accepted_consent = st.checkbox(
        "Acepto el uso confidencial de mis datos y comprendo que esta "
        "herramienta no reemplaza la consulta médica.",
        key="informed_consent_checkbox",
    )
    def continue_from_consent() -> bool:
        if not accepted_consent:
            st.error("Debe aceptar el consentimiento informado para continuar.")
            return False
        st.session_state["informed_consent_accepted"] = True
        return True

    render_patient_navigation(
        "welcome",
        on_next=continue_from_consent,
        next_step="initial",
    )


def render_initial_classification() -> None:
    """Capture the initial area of interest for the current session."""
    hide_sidebar()
    st.title("¿Qué desea mejorar?")

    selected_category = st.radio(
        "Área de interés",
        [
            "Dolor y movilidad",
            "Insomnio",
            "Estrés o ansiedad",
            "Tristeza o depresión",
            "Respiración",
            "Digestión",
            "Salud urinaria, próstata o ginecológica",
            "Otro problema de salud",
        ],
        index=None,
        key="initial_category_selection",
        label_visibility="collapsed",
    )
    other_health_problem_description = ""
    if selected_category == "Otro problema de salud":
        other_health_problem_description = st.text_area(
            "Por favor describa brevemente el motivo de consulta",
            max_chars=500,
            key="other_health_problem_description_input",
        )
        show_dictation_help()

    def continue_from_initial() -> bool:
        if selected_category is None:
            st.error("Seleccione una opción para continuar.")
            return False
        if (
            selected_category == "Otro problema de salud"
            and not other_health_problem_description.strip()
        ):
            st.error("Por favor complete este campo para continuar.")
            return False
        st.session_state["selected_initial_category"] = selected_category
        if selected_category == "Otro problema de salud":
            st.session_state["other_health_problem_description"] = (
                other_health_problem_description.strip()
            )
        return True

    render_patient_navigation(
        "consent",
        on_next=continue_from_initial,
        next_step="personal_data",
    )


def render_personal_data_step() -> None:
    """Collect simple personal data for the guided experience."""
    hide_sidebar()
    st.title("Datos personales")
    st.success("Perfecto. Vamos a completar una breve evaluación.")
    existing_patient_selected = bool(
        st.session_state.get("selected_existing_patient_id")
    )
    if existing_patient_selected:
        st.info(
            "Paciente existente seleccionado. No es necesario volver a mostrar "
            "DNI ni teléfono completos."
        )

    saved_personal_data = st.session_state.get("guided_personal_data", {})
    guided_name = st.text_input(
        "Apellido y nombre completo *",
        value=saved_personal_data.get("name", ""),
        max_chars=120,
    )
    guided_dni = st.text_input(
        "DNI *",
        value=saved_personal_data.get("dni", ""),
        max_chars=30,
    )
    guided_phone = st.text_input(
        "Teléfono celular / WhatsApp o contacto de familiar *",
        value=saved_personal_data.get("phone", ""),
        max_chars=60,
    )
    guided_email = st.text_input(
        "E-mail",
        value=saved_personal_data.get("email", ""),
        max_chars=120,
    )
    guided_age = st.text_input(
        "Edad *",
        value=str(saved_personal_data.get("age", "")),
        max_chars=3,
    )
    sex_options = [
        "Femenino",
        "Masculino",
        "Intersexual",
        "Otro",
        "Prefiere no informar",
    ]
    saved_sex = saved_personal_data.get("sex")
    guided_sex = st.selectbox(
        "Sexo *",
        sex_options,
        index=option_index(
            sex_options,
            (
                saved_sex
                if saved_sex in sex_options
                else "Otro" if saved_sex else None
            ),
        ),
        placeholder="Seleccione una opción",
    )
    guided_sex_other = ""
    if guided_sex == "Otro":
        guided_sex_other = st.text_input(
            "Por favor especifique",
            value=(
                saved_sex or ""
                if saved_sex not in sex_options
                else ""
            ),
            max_chars=80,
        )

    def continue_from_personal_data() -> bool:
        needs_identity_fields = not existing_patient_selected
        if (
            not guided_name.strip()
            or (needs_identity_fields and not guided_dni.strip())
            or (needs_identity_fields and not guided_phone.strip())
            or not guided_age.strip().isdigit()
            or int(guided_age.strip()) > 120
            or not guided_sex
        ):
            st.error("Complete los datos obligatorios para continuar.")
            return False
        if guided_sex == "Otro" and not guided_sex_other.strip():
            st.error("Por favor complete este campo para continuar.")
            return False
        st.session_state["guided_personal_data"] = {
            "name": guided_name.strip(),
            "age": int(guided_age.strip()),
            "sex": guided_sex_other.strip() if guided_sex == "Otro" else guided_sex,
            "dni": guided_dni.strip(),
            "phone": guided_phone.strip(),
            "email": guided_email.strip(),
        }
        return True

    render_patient_navigation(
        "initial",
        on_next=continue_from_personal_data,
        next_step="problem_details",
    )


def render_problem_details_step() -> None:
    """Collect the main problem in patient-friendly language."""
    hide_sidebar()
    st.title("Cuéntenos su problema")

    selected_category = st.session_state.get("selected_initial_category", "")
    duration_options = [
        "Menos de 1 semana",
        "Menos de 1 mes",
        "Más de 3 meses",
        "Más de 1 año",
    ]
    saved_problem_details = st.session_state.get("guided_problem_details", {})
    category_fields = {
        "Insomnio": {
            "label": "¿Qué problema tiene con el sueño?",
            "options": [
                "Me cuesta dormir",
                "Me despierto varias veces",
                "Me despierto muy temprano",
                "Duermo pero no descanso",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Estrés o ansiedad": {
            "label": "¿Qué siente principalmente?",
            "options": [
                "Nerviosismo",
                "Preocupación excesiva",
                "Palpitaciones o tensión",
                "Ataques de ansiedad",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Tristeza o depresión": {
            "label": "¿Qué siente principalmente?",
            "options": [
                "Tristeza",
                "Falta de ganas",
                "Cansancio emocional",
                "Pérdida de interés",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Respiración": {
            "label": "¿Cuál es el problema principal?",
            "options": [
                "Falta de aire",
                "Tos",
                "Alergia respiratoria",
                "Asma",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Digestión": {
            "label": "¿Cuál es el problema principal?",
            "options": [
                "Acidez o reflujo",
                "Distensión abdominal",
                "Estreñimiento",
                "Diarrea",
                "Náuseas",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Salud urinaria, próstata o ginecológica": {
            "label": "¿Cuál es el problema principal?",
            "options": [
                "Orinar frecuentemente",
                "Ardor al orinar",
                "Dolor pélvico",
                "Síntomas prostáticos",
                "Síntomas ginecológicos",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
    }

    with st.form("guided_problem_details_form"):
        if selected_category == "Otro problema de salud":
            problem = st.session_state.get("other_health_problem_description", "")
            st.write(f"**Problema o síntoma principal:** {problem}")
        elif selected_category == "Dolor y movilidad":
            problem = st.text_input(
                "¿Cuál es el problema que desea tratar?",
                value=saved_problem_details.get("problem", ""),
                placeholder=(
                    "Ejemplo: dolor lumbar, dolor de rodilla, dolor cervical."
                ),
            )
            slider_label = "¿Qué intensidad tiene hoy?"
            caption = "0 = nada, 10 = máximo."
        else:
            field_config = category_fields.get(selected_category, {})
            problem = st.selectbox(
                field_config.get("label", "¿Cuál es el problema principal?"),
                field_config.get("options", ["Otro"]),
                index=option_index(
                    field_config.get("options", ["Otro"]),
                    saved_problem_details.get("problem"),
                ),
                placeholder="Seleccione una opción",
            )
            slider_label = field_config.get(
                "slider_label",
                "¿Cuánto afecta su vida diaria?",
            )
            caption = field_config.get("caption", "0 = nada, 10 = muchísimo.")

        if selected_category == "Otro problema de salud":
            slider_label = "¿Cuánto afecta su vida diaria?"
            caption = "0 = nada, 10 = muchísimo."

        duration = st.selectbox(
            "¿Hace cuánto tiempo lo tiene?",
            duration_options,
            index=option_index(duration_options, saved_problem_details.get("duration")),
            placeholder="Seleccione una opción",
        )
        intensity = st.slider(
            slider_label,
            min_value=0,
            max_value=10,
            value=int(saved_problem_details.get("intensity", 0)),
            help=caption,
        )
        st.caption(caption)
        submitted = st.form_submit_button(
            "Guardar información",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        problem_text = problem.strip() if isinstance(problem, str) else problem
        if not problem_text or not duration:
            st.error("Complete el problema y el tiempo de evolución.")
            return
        st.session_state["guided_problem_details"] = {
            "problem": problem_text,
            "duration": duration,
            "intensity": int(intensity),
        }
        st.session_state["guided_step"] = "follow_up_orientation"
        st.rerun()




def ensure_guided_evaluations_table() -> None:
    """Create and migrate the intake-results table from this application file."""
    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS guided_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                completed_at TEXT NOT NULL,
                name TEXT NOT NULL,
                has_dni INTEGER NOT NULL DEFAULT 0,
                has_contact INTEGER NOT NULL DEFAULT 0,
                dni TEXT,
                phone TEXT,
                email TEXT,
                consultation_type TEXT,
                main_reason TEXT,
                main_problem TEXT,
                duration TEXT,
                current_impact REAL,
                global_functional_score REAL,
                daily_limitation TEXT,
                medication_related TEXT,
                medication_name TEXT,
                treatment_expectations TEXT NOT NULL DEFAULT '[]'
            )
            """
        )
        existing_columns = {row[1] for row in connection.execute("PRAGMA table_info(guided_evaluations)").fetchall()}
        for column_name in ("dni", "phone", "email", "consultation_type"):
            if column_name not in existing_columns:
                connection.execute(f"ALTER TABLE guided_evaluations ADD COLUMN {column_name} TEXT")
        if "therapeutic_cycle_id" not in existing_columns:
            connection.execute(
                "ALTER TABLE guided_evaluations ADD COLUMN therapeutic_cycle_id INTEGER"
            )


def ensure_therapeutic_cycles_schema() -> None:
    """Create therapeutic-cycle storage and attach legacy sessions safely."""
    ensure_guided_evaluations_table()
    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS therapeutic_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                fecha_inicio TEXT NOT NULL,
                tipo_consulta TEXT NOT NULL,
                main_reason TEXT,
                main_problem TEXT,
                status TEXT NOT NULL DEFAULT 'activo'
                    CHECK (status IN ('activo', 'cerrado')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
            """
        )
        session_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(sessions)").fetchall()
        }
        if "therapeutic_cycle_id" not in session_columns:
            connection.execute(
                "ALTER TABLE sessions ADD COLUMN therapeutic_cycle_id INTEGER"
            )

        patients = connection.execute(
            """
            SELECT id, created_at, clinical_category, diagnosis, main_complaint
            FROM patients
            ORDER BY id
            """
        ).fetchall()
        for patient in patients:
            existing_cycle = connection.execute(
                """
                SELECT id
                FROM therapeutic_cycles
                WHERE patient_id = ?
                ORDER BY id
                LIMIT 1
                """,
                (int(patient["id"]),),
            ).fetchone()
            if existing_cycle is None:
                first_session = connection.execute(
                    """
                    SELECT date
                    FROM sessions
                    WHERE patient_id = ?
                    ORDER BY date ASC, session_number ASC, id ASC
                    LIMIT 1
                    """,
                    (int(patient["id"]),),
                ).fetchone()
                fecha_inicio = (
                    first_session["date"]
                    if first_session and first_session["date"]
                    else str(patient["created_at"] or date.today().isoformat())[:10]
                )
                connection.execute(
                    """
                    INSERT INTO therapeutic_cycles (
                        patient_id, fecha_inicio, tipo_consulta,
                        main_reason, main_problem, status
                    ) VALUES (?, ?, ?, ?, ?, 'activo')
                    """,
                    (
                        int(patient["id"]),
                        fecha_inicio,
                        "Consulta inicial actual",
                        patient["clinical_category"] or patient["diagnosis"],
                        patient["main_complaint"],
                    ),
                )

        unassigned_sessions = connection.execute(
            """
            SELECT id, patient_id
            FROM sessions
            WHERE therapeutic_cycle_id IS NULL
            ORDER BY patient_id, session_number, date, id
            """
        ).fetchall()
        for session in unassigned_sessions:
            cycle = connection.execute(
                """
                SELECT id
                FROM therapeutic_cycles
                WHERE patient_id = ?
                ORDER BY id
                LIMIT 1
                """,
                (int(session["patient_id"]),),
            ).fetchone()
            if cycle:
                connection.execute(
                    """
                    UPDATE sessions
                    SET therapeutic_cycle_id = ?
                    WHERE id = ?
                    """,
                    (int(cycle["id"]), int(session["id"])),
                )


def get_patient_cycles(patient_id: int, *, active_only: bool = False) -> list[dict]:
    """Return therapeutic cycles for one patient."""
    ensure_therapeutic_cycles_schema()
    where_status = "AND status = 'activo'" if active_only else ""
    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"""
            SELECT *
            FROM therapeutic_cycles
            WHERE patient_id = ?
            {where_status}
            ORDER BY fecha_inicio DESC, id DESC
            """,
            (patient_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_therapeutic_cycle(
    patient_id: int,
    consultation_type: str,
    main_reason: str,
    main_problem: str,
    *,
    status: str = "activo",
) -> int:
    """Create a therapeutic cycle for a patient and return its identifier."""
    with sqlite3.connect(database_module.DB_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO therapeutic_cycles (
                patient_id, fecha_inicio, tipo_consulta,
                main_reason, main_problem, status
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                date.today().isoformat(),
                consultation_type,
                main_reason,
                main_problem,
                status,
            ),
        )
        return int(cursor.lastrowid)


def assign_session_to_cycle(session_id: int, cycle_id: int) -> None:
    """Attach an existing session record to a therapeutic cycle."""
    ensure_therapeutic_cycles_schema()
    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.execute(
            "UPDATE sessions SET therapeutic_cycle_id = ? WHERE id = ?",
            (cycle_id, session_id),
        )


def close_therapeutic_cycle(cycle_id: int) -> None:
    """Mark a therapeutic cycle as closed after clinical discharge."""
    ensure_therapeutic_cycles_schema()
    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.execute(
            "UPDATE therapeutic_cycles SET status = 'cerrado' WHERE id = ?",
            (cycle_id,),
        )


def get_cycle_sessions(cycle_id: int) -> pd.DataFrame:
    """Return sessions associated with one therapeutic cycle."""
    ensure_therapeutic_cycles_schema()
    with sqlite3.connect(database_module.DB_PATH) as connection:
        return pd.read_sql_query(
            """
            SELECT *
            FROM sessions
            WHERE therapeutic_cycle_id = ?
            ORDER BY session_number ASC, date ASC, id ASC
            """,
            connection,
            params=(cycle_id,),
        )


def cycle_label(cycle: dict) -> str:
    """Build a visible cycle label without exposing direct identifiers."""
    fecha_inicio = cycle.get("fecha_inicio") or "Sin fecha"
    motivo = fix_visible_encoding(cycle.get("main_reason") or "Sin motivo")
    problema = fix_visible_encoding(cycle.get("main_problem") or "Sin problema")
    status = cycle.get("status") or "activo"
    return f"Ciclo {cycle['id']} · {fecha_inicio} · {motivo} · {problema} · {status}"


def find_existing_patient_for_guided_data(personal_data: dict) -> int | None:
    """Find an already registered patient using exact DNI, phone, or name."""
    patients = get_patients()
    if patients.empty:
        return None

    dni = str(personal_data.get("dni") or "").strip()
    phone_digits = "".join(
        character for character in str(personal_data.get("phone") or "")
        if character.isdigit()
    )
    name = str(personal_data.get("name") or "").strip().casefold()

    for _, row in patients.iterrows():
        row_dni = str(row.get("dni") or "").strip()
        row_phone_digits = "".join(
            character for character in str(row.get("phone") or "")
            if character.isdigit()
        )
        row_name = str(row.get("name") or "").strip().casefold()
        if dni and row_dni == dni:
            return int(row["id"])
        if phone_digits and row_phone_digits == phone_digits:
            return int(row["id"])
        if name and row_name == name:
            return int(row["id"])
    return None


def ensure_patient_for_guided_evaluation(
    personal_data: dict,
    problem_details: dict,
) -> int:
    """Use the selected patient or create one for a completed intake."""
    selected_patient_id = st.session_state.get("selected_existing_patient_id")
    if selected_patient_id:
        return int(selected_patient_id)

    existing_patient_id = find_existing_patient_for_guided_data(personal_data)
    if existing_patient_id:
        return existing_patient_id

    age_value = str(personal_data.get("age") or "0").strip()
    patient_id = add_patient(
        name=str(personal_data.get("name") or "Sin nombre"),
        dni=str(personal_data.get("dni") or f"EVAL-{datetime.now().timestamp():.0f}"),
        age=int(age_value) if age_value.isdigit() else 0,
        sex=str(personal_data.get("sex") or "Sin completar"),
        phone=str(personal_data.get("phone") or personal_data.get("email") or ""),
        diagnosis=str(problem_details.get("problem") or "Sin completar"),
        main_complaint=str(problem_details.get("problem") or "Sin completar"),
        assigned_scale="EVA",
        clinical_category=str(
            st.session_state.get("selected_initial_category", "Sin completar")
        ),
        clinical_subcategory=str(problem_details.get("problem") or "Sin completar"),
        suggested_prom="Pendiente de clasificacion",
        care_origin="Pendiente de clasificacion",
    )
    return int(patient_id)


def load_completed_guided_evaluations() -> list[dict]:
    """Load completed patient-flow evaluations for the professional panel."""
    ensure_guided_evaluations_table()
    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM guided_evaluations ORDER BY completed_at DESC, id DESC").fetchall()
    evaluations = []
    for row in rows:
        try:
            expectations = json.loads(row["treatment_expectations"] or "[]")
        except (TypeError, json.JSONDecodeError):
            expectations = []
        evaluations.append({
            "Evaluación ID": f"EVAL-{row['id']:06d}",
            "Fecha/hora": row["completed_at"],
            "Nombre": row["name"],
            "DNI": "registrado" if row["has_dni"] else "no registrado",
            "Contacto": "registrado" if row["has_contact"] else "no registrado",
            "Tipo de consulta": row["consultation_type"] or "Paciente nuevo",
            "Motivo principal": row["main_reason"],
            "Problema o síntoma principal": row["main_problem"],
            "Tiempo de evolución": row["duration"],
            "Impacto actual": row["current_impact"],
            "Estado general últimos 7 días": row["global_functional_score"],
            "Limitación diaria": row["daily_limitation"],
            "Medicación relacionada": row["medication_related"],
            "Medicamento informado": row["medication_name"],
            "Objetivos principales seleccionados": expectations,
        })
    return evaluations


def store_completed_guided_evaluation() -> None:
    """Persist one completed patient-flow evaluation for the panel."""
    if st.session_state.get("guided_evaluation_recorded"):
        return
    personal_data = st.session_state.get("guided_personal_data", {})
    problem_details = st.session_state.get("guided_problem_details", {})
    follow_up_orientation = st.session_state.get("guided_follow_up_orientation", {})
    treatment_expectations = st.session_state.get("guided_treatment_expectations", {})
    medication_value = follow_up_orientation.get("medication_related")
    if medication_value in {"No", "Sí", "No estoy seguro/a"}:
        medication_related = medication_value
        medication_name = None
    elif medication_value:
        medication_related = "Sí"
        medication_name = medication_value
    else:
        medication_related = "Sin completar"
        medication_name = None
    ensure_guided_evaluations_table()
    patient_id = ensure_patient_for_guided_evaluation(personal_data, problem_details)
    cycle_id = create_therapeutic_cycle(
        patient_id=patient_id,
        consultation_type=st.session_state.get("tipo_consulta", "Paciente nuevo"),
        main_reason=st.session_state.get("selected_initial_category", "Sin completar"),
        main_problem=problem_details.get("problem", "Sin completar"),
    )
    st.session_state["current_therapeutic_cycle_id"] = cycle_id
    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO guided_evaluations (
                completed_at, name, has_dni, has_contact, dni, phone, email,
                consultation_type, main_reason, main_problem, duration,
                current_impact, global_functional_score, daily_limitation,
                medication_related, medication_name, treatment_expectations,
                therapeutic_cycle_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="minutes"),
                personal_data.get("name", "Sin completar"),
                int(bool(personal_data.get("dni"))),
                int(bool(personal_data.get("phone") or personal_data.get("email"))),
                personal_data.get("dni"),
                personal_data.get("phone"),
                personal_data.get("email"),
                st.session_state.get("tipo_consulta", "Paciente nuevo"),
                st.session_state.get("selected_initial_category", "Sin completar"),
                problem_details.get("problem", "Sin completar"),
                problem_details.get("duration", "Sin completar"),
                problem_details.get("intensity"),
                st.session_state.get("global_functional_score"),
                follow_up_orientation.get("daily_limitation", "Sin completar"),
                medication_related,
                medication_name,
                json.dumps(treatment_expectations.get("expectations", []), ensure_ascii=False),
                cycle_id,
            ),
        )
    st.session_state["guided_evaluation_recorded"] = True



def _search_text_matches(query: str, *values: object) -> bool:
    """Match names normally and identifiers ignoring phone punctuation."""
    normalized_query = query.strip().casefold()
    query_digits = "".join(character for character in query if character.isdigit())
    for value in values:
        normalized_value = str(value or "").strip().casefold()
        if normalized_query and normalized_query in normalized_value:
            return True
        value_digits = "".join(character for character in normalized_value if character.isdigit())
        if query_digits and query_digits in value_digits:
            return True
    return False


def search_followup_patients(query: str) -> list[dict]:
    """Find patients for follow-up from registered patients and guided evaluations."""
    patients = get_patients()
    matches = []
    matched_patient_ids: set[int] = set()

    def add_match(row: pd.Series) -> None:
        patient_id = int(row["id"])
        if patient_id in matched_patient_ids:
            return
        matched_patient_ids.add(patient_id)
        code = row.get("patient_code") or f"P-{patient_id:04d}"
        matches.append(
            {
                "id": patient_id,
                "name": row.get("name", "Sin nombre"),
                "label": f"{row.get('name', 'Sin nombre')} - {code}",
            }
        )

    for _, row in patients.iterrows():
        if _search_text_matches(
            query,
            row.get("name"),
            row.get("dni"),
            row.get("phone"),
            row.get("patient_code"),
        ):
            add_match(row)

    ensure_guided_evaluations_table()
    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        guided_rows = connection.execute(
            """
            SELECT *
            FROM guided_evaluations
            ORDER BY completed_at DESC, id DESC
            """
        ).fetchall()

    for guided_row in guided_rows:
        if _search_text_matches(
            query,
            guided_row["name"],
            guided_row["dni"],
            guided_row["phone"],
            guided_row["email"],
        ):
            existing_patients = get_patients()
            if not existing_patients.empty:
                guided_dni = str(guided_row["dni"] or "").strip()
                guided_name = str(guided_row["name"] or "").strip().casefold()
                guided_phone = str(guided_row["phone"] or "").strip()
                same_patient_mask = (
                    existing_patients["name"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .str.casefold()
                    == guided_name
                )
                if guided_dni:
                    same_patient_mask = same_patient_mask | (
                        existing_patients["dni"].fillna("").astype(str).str.strip()
                        == guided_dni
                    )
                if guided_phone:
                    same_patient_mask = same_patient_mask | (
                        existing_patients["phone"].fillna("").astype(str).str.strip()
                        == guided_phone
                    )
                same_patient = existing_patients[same_patient_mask]
                if not same_patient.empty:
                    add_match(same_patient.iloc[0])
                    continue

            guided_id = int(guided_row["id"])
            patient_id = add_patient(
                name=str(guided_row["name"] or "Sin nombre"),
                dni=str(guided_row["dni"] or f"EVAL-{guided_id:06d}"),
                age=0,
                sex="Sin completar",
                phone=str(guided_row["phone"] or guided_row["email"] or ""),
                diagnosis=str(
                    guided_row["main_problem"]
                    or guided_row["main_reason"]
                    or "Sin completar"
                ),
                main_complaint=str(guided_row["main_problem"] or "Sin completar"),
                assigned_scale="EVA",
                clinical_category=str(guided_row["main_reason"] or "Sin completar"),
                clinical_subcategory=str(
                    guided_row["main_problem"] or "Sin completar"
                ),
                suggested_prom="Pendiente de clasificacion",
                care_origin="Pendiente de clasificacion",
            )
            create_therapeutic_cycle(
                patient_id=patient_id,
                consultation_type=guided_row["consultation_type"]
                or "Consulta inicial actual",
                main_reason=guided_row["main_reason"] or "Sin completar",
                main_problem=guided_row["main_problem"] or "Sin completar",
            )
            refreshed_patients = get_patients()
            created_patient = refreshed_patients.loc[
                refreshed_patients["id"] == patient_id
            ].iloc[0]
            add_match(created_patient)

    return sorted(matches, key=lambda patient: patient["label"].casefold())


def render_returning_patient_search_step() -> None:
    """Select an existing patient before starting a new therapeutic cycle."""
    hide_sidebar()
    st.title("Nueva consulta de paciente ya registrado")
    st.write(
        "Busque el paciente existente para iniciar una evaluación completa "
        "como nuevo ciclo terapéutico."
    )

    search_query = st.text_input(
        "Buscar paciente por DNI, nombre o teléfono/contacto",
        key="returning_patient_search_query",
    )
    if st.button("Buscar paciente", type="primary", use_container_width=True):
        if not search_query.strip():
            st.error("Ingrese DNI, nombre o teléfono/contacto para buscar.")
        else:
            st.session_state["returning_patient_search_results"] = (
                search_followup_patients(search_query)
            )

    results = st.session_state.get("returning_patient_search_results")
    selected_label = None
    if results is not None:
        if not results:
            st.warning("No encontramos un paciente registrado con esos datos.")
        else:
            selected_label = st.selectbox(
                "Seleccione paciente",
                [patient["label"] for patient in results],
                key="returning_patient_selected_label",
            )
            selected_patient = next(
                patient for patient in results if patient["label"] == selected_label
            )
            cycles = get_patient_cycles(int(selected_patient["id"]))
            st.info(f"Ciclos registrados para este paciente: {len(cycles)}")

    back_column, continue_column = st.columns(2)
    with back_column:
        if st.button("Atrás", use_container_width=True):
            clear_returning_patient_flow()
            st.session_state["guided_step"] = "welcome"
            st.rerun()
    with continue_column:
        if results and st.button(
            "Iniciar nueva consulta",
            type="primary",
            use_container_width=True,
        ):
            selected_patient = next(
                patient for patient in results if patient["label"] == selected_label
            )
            patient = get_patient(int(selected_patient["id"]))
            st.session_state["selected_existing_patient_id"] = int(
                selected_patient["id"]
            )
            st.session_state["guided_personal_data"] = {
                "name": patient["name"] if patient else selected_patient["name"],
                "dni": "",
                "phone": "",
                "email": "",
                "age": int(patient["age"]) if patient else "",
                "sex": patient["sex"] if patient else "",
            }
            st.session_state["tipo_consulta"] = (
                "Nueva consulta de paciente ya registrado"
            )
            st.session_state["new_problem_existing_patient"] = True
            st.session_state["guided_step"] = "consent"
            st.rerun()


def clear_returning_patient_flow() -> None:
    """Clear temporary returning-patient search data."""
    for key in (
        "returning_patient_search_query",
        "returning_patient_search_results",
        "returning_patient_selected_label",
        "selected_existing_patient_id",
        "current_therapeutic_cycle_id",
    ):
        st.session_state.pop(key, None)


def format_sessions_for_followup(sessions: pd.DataFrame) -> pd.DataFrame:
    """Prepare the existing session records for patient-facing/professional views."""
    if sessions.empty:
        return pd.DataFrame(
            columns=[
                "Sesión",
                "Fecha",
                "Intensidad actual",
                "Estado general últimos 7 días",
                "Cambio de medicación",
                "Molestias posteriores",
                "Comentario",
            ]
        )

    table = pd.DataFrame(
        {
            "Sesión": sessions["session_number"],
            "Fecha": pd.to_datetime(sessions["date"], errors="coerce").dt.strftime(
                "%d/%m/%Y"
            ),
            "Intensidad actual": sessions["eva_pre"],
            "Estado general últimos 7 días": sessions["functional_impact"],
            "Cambio de medicación": sessions["analgesic_change"],
            "Molestias posteriores": sessions["adverse_event_severity"],
            "Comentario": sessions["notes"].fillna("") if "notes" in sessions else "",
        }
    )
    for column in table.select_dtypes(include="object").columns:
        table[column] = table[column].map(fix_visible_encoding)
    return table


def render_followup_search_step() -> None:
    """Find an existing patient and show their current session history."""
    hide_sidebar()
    st.title("Seguimiento de evolución")
    st.write(
        "Complete esta breve evaluación para informar cómo evolucionó desde la "
        "última consulta."
    )

    search_query = st.text_input(
        "Buscar paciente por DNI, nombre o teléfono/contacto",
        key="followup_search_query",
    )
    if st.button("Buscar paciente", type="primary", use_container_width=True):
        if not search_query.strip():
            st.error("Ingrese DNI, nombre o teléfono/contacto para buscar.")
        else:
            st.session_state["followup_search_results"] = search_followup_patients(
                search_query
            )

    results = st.session_state.get("followup_search_results")
    selected_label = None
    if results is not None:
        if not results:
            st.warning("No encontramos un paciente registrado con esos datos.")
        else:
            selected_label = st.selectbox(
                "Seleccione paciente",
                [patient["label"] for patient in results],
                key="followup_selected_label",
            )
            selected_patient = next(
                patient for patient in results if patient["label"] == selected_label
            )
            active_cycles = get_patient_cycles(
                int(selected_patient["id"]),
                active_only=True,
            )
            if not active_cycles:
                st.warning(
                    "Este paciente no tiene ciclos terapéuticos activos. "
                    "Inicie una nueva consulta para abrir un ciclo."
                )
            else:
                selected_cycle_label = st.selectbox(
                    "Seleccione ciclo terapéutico activo",
                    [cycle_label(cycle) for cycle in active_cycles],
                    key="followup_selected_cycle_label",
                )
                selected_cycle = next(
                    cycle
                    for cycle in active_cycles
                    if cycle_label(cycle) == selected_cycle_label
                )
                sessions = get_cycle_sessions(int(selected_cycle["id"]))
                st.markdown("**Seguimientos registrados en este ciclo**")
                if sessions.empty:
                    st.info("Este ciclo todavía no tiene seguimientos registrados.")
                else:
                    st.dataframe(
                        format_sessions_for_followup(sessions),
                        hide_index=True,
                        use_container_width=True,
                    )

    back_column, continue_column = st.columns(2)
    with back_column:
        if st.button("Atrás", use_container_width=True):
            st.session_state["guided_step"] = "welcome"
            st.rerun()
    with continue_column:
        if results and st.button(
            "Registrar nuevo seguimiento",
            type="primary",
            use_container_width=True,
        ):
            selected_patient = next(
                patient for patient in results if patient["label"] == selected_label
            )
            active_cycles = get_patient_cycles(
                int(selected_patient["id"]),
                active_only=True,
            )
            selected_cycle_label = st.session_state.get("followup_selected_cycle_label")
            selected_cycle = next(
                (
                    cycle
                    for cycle in active_cycles
                    if cycle_label(cycle) == selected_cycle_label
                ),
                None,
            )
            if selected_cycle is None:
                st.error("Seleccione un ciclo terapéutico activo.")
                return
            st.session_state["followup_patient"] = selected_patient
            st.session_state["followup_cycle"] = selected_cycle
            st.session_state["guided_step"] = "followup_form"
            st.rerun()


def render_followup_form_step() -> None:
    """Register the brief evolution as a new existing session."""
    hide_sidebar()
    patient = st.session_state.get("followup_patient")
    if not patient:
        st.session_state["guided_step"] = "followup_search"
        st.rerun()
    cycle = st.session_state.get("followup_cycle")
    if not cycle:
        st.session_state["guided_step"] = "followup_search"
        st.rerun()

    patient_id = int(patient["id"])
    all_sessions = get_patient_sessions(patient_id)
    cycle_sessions = get_cycle_sessions(int(cycle["id"]))
    next_session_number = (
        int(all_sessions["session_number"].max()) + 1
        if not all_sessions.empty
        else 1
    )

    st.title("Seguimiento de evolución")
    st.caption(f"Paciente seleccionado: {patient['name']}")
    st.caption(f"Ciclo seleccionado: {cycle_label(cycle)}")
    st.markdown("**Seguimientos de este ciclo**")
    if cycle_sessions.empty:
        st.info("Este ciclo todavía no tiene seguimientos registrados.")
    else:
        st.dataframe(
            format_sessions_for_followup(cycle_sessions),
            hide_index=True,
            use_container_width=True,
        )

    with st.form("patient_followup_session_form"):
        st.write(f"**Nueva sesión:** {next_session_number}")
        session_date = st.date_input(
            "Fecha",
            value=date.today(),
            max_value=date.today(),
        )
        comparison = st.radio(
            "¿Cómo se siente comparado con la última consulta?",
            ["Mucho mejor", "Algo mejor", "Igual", "Peor"],
            index=None,
        )
        symptom_intensity = st.slider(
            "Intensidad actual del problema principal",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
        )
        global_score = st.slider(
            "Estado general últimos 7 días",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.5,
        )
        medication_change = st.radio(
            "¿Cambió la medicación?",
            ["No", "Disminuyó", "Aumentó", "Suspendió", "No sabe"],
            index=None,
        )
        post_session_discomfort = st.radio(
            "¿Tuvo alguna molestia luego de la sesión anterior?",
            ["No", "Sí, leve", "Sí, moderada", "Sí, intensa"],
            index=None,
        )
        free_comment = st.text_area("Comentario libre", max_chars=1200)
        st.caption("Puede escribir o dictar desde el micrófono del celular.")

        back_column, save_column = st.columns(2)
        back_pressed = back_column.form_submit_button(
            "Atrás", use_container_width=True
        )
        save_pressed = save_column.form_submit_button(
            "Guardar seguimiento",
            type="primary",
            use_container_width=True,
        )

    if back_pressed:
        st.session_state["guided_step"] = "followup_search"
        st.rerun()
    if save_pressed:
        if not comparison or not medication_change or not post_session_discomfort:
            st.error("Complete todas las opciones antes de guardar.")
            return
        if session_number_exists(patient_id, next_session_number):
            st.error("Ese número de sesión ya existe para el paciente.")
            return

        adverse_event_severity = {
            "No": "Ninguno",
            "Sí, leve": "Leve",
            "Sí, moderada": "Moderado",
            "Sí, intensa": "Severo",
        }[post_session_discomfort]
        adverse_description = (
            post_session_discomfort if post_session_discomfort != "No" else ""
        )
        notes = (
            f"Evolución comparada con la última consulta: {comparison}\n"
            f"Cambio de medicación: {medication_change}\n"
            f"Molestias posteriores: {post_session_discomfort}\n"
            f"Comentario libre: {free_comment.strip() or 'Sin comentario'}"
        )
        pgic_map = {
            "Mucho mejor": 1,
            "Algo mejor": 2,
            "Igual": 4,
            "Peor": 6,
        }

        try:
            session_id = add_session(
                patient_id=patient_id,
                session_number=next_session_number,
                date=session_date.isoformat(),
                eva_pre=float(symptom_intensity),
                eva_post=float(symptom_intensity),
                pgic=pgic_map[comparison],
                functional_impact=float(global_score),
                medication_name="",
                medication_frequency="",
                analgesic_change=medication_change,
                adverse_event_severity=adverse_event_severity,
                adverse_event_description=adverse_description,
                notes=notes,
            )
            assign_session_to_cycle(session_id, int(cycle["id"]))
        except sqlite3.Error as error:
            st.error(f"No se pudo guardar el seguimiento: {error}")
            return
        st.session_state["guided_step"] = "followup_complete"
        st.rerun()

def clear_followup_flow() -> None:
    """Clear temporary follow-up navigation data."""
    for key in (
        "followup_search_query",
        "followup_search_results",
        "followup_selected_label",
        "followup_selected_cycle_label",
        "followup_patient",
        "followup_cycle",
        "tipo_consulta",
    ):
        st.session_state.pop(key, None)


def render_followup_complete_step() -> None:
    """Confirm that the evolution record was stored."""
    hide_sidebar()
    st.success("Seguimiento registrado correctamente.")
    if st.button("Volver al inicio", type="primary", use_container_width=True):
        clear_followup_flow()
        st.session_state["guided_step"] = "welcome"
        st.rerun()

def render_thanks_step() -> None:
    """Render the patient-friendly summary before the final closure."""
    hide_sidebar()

    personal_data = st.session_state.get("guided_personal_data", {})
    problem_details = st.session_state.get("guided_problem_details", {})
    follow_up_orientation = st.session_state.get(
        "guided_follow_up_orientation",
        {},
    )
    adaptive_details = st.session_state.get("guided_adaptive_details", {})
    treatment_expectations = st.session_state.get(
        "guided_treatment_expectations",
        {},
    )
    st.title("RESUMEN")
    st.write(
        "Revise la información cargada. Si necesita corregir algo, presione "
        "Atrás."
    )
    consultation_type = st.session_state.get(
        "tipo_consulta",
        "Paciente nuevo",
    )
    st.write(f"**Tipo de consulta:** {consultation_type}")
    st.write(
        f"**Motivo principal:** "
        f"{st.session_state.get('selected_initial_category', 'Sin completar')}"
    )
    st.write(f"**Nombre:** {personal_data.get('name', 'Sin completar')}")
    st.write(
        f"**DNI:** "
        f"{'registrado' if personal_data.get('dni') else 'no registrado'}"
    )
    st.write(
        f"**Contacto:** "
        f"{'registrado' if personal_data.get('phone') else 'no registrado'}"
    )
    st.write(
        f"**E-mail:** "
        f"{'registrado' if personal_data.get('email') else 'no registrado'}"
    )
    st.write(
        f"**Problema o síntoma principal:** "
        f"{problem_details.get('problem', 'Sin completar')}"
    )
    st.write(
        f"**Tiempo de evolución:** "
        f"{problem_details.get('duration', 'Sin completar')}"
    )
    intensity = problem_details.get("intensity", "Sin completar")
    st.write(f"**Impacto actual:** {intensity} de 10")
    st.write(
        f"**Empeora con:** "
        f"{follow_up_orientation.get('worsens_with', 'Sin completar')}"
    )
    st.write(
        f"**Mejora con:** "
        f"{follow_up_orientation.get('improves_with', 'Sin completar')}"
    )
    st.write(
        f"**Medicación relacionada:** "
        f"{follow_up_orientation.get('medication_related', 'Sin completar')}"
    )
    st.write(
        f"**Limitación diaria:** "
        f"{follow_up_orientation.get('daily_limitation', 'Sin completar')}"
    )
    for item in adaptive_details.values():
        st.write(f"**{item['question']}** {item['answer']}")
    expectations = treatment_expectations.get("expectations", [])
    expectations_text = (
        ", ".join(expectations)
        if expectations
        else "Sin completar"
    )
    st.write(f"**Objetivos principales seleccionados:** {expectations_text}")
    st.write(
        f"**Expectativa expresada libremente:** "
        f"{treatment_expectations.get('daily_life_result', 'Sin completar')}"
    )

    def finish_guided_flow() -> bool:
        store_completed_guided_evaluation()
        st.session_state["guided_step"] = "final_closure"
        return True

    render_patient_navigation(
        "treatment_expectations",
        next_label="Finalizar",
        on_next=finish_guided_flow,
    )

def render_problem_details_step() -> None:
    """Collect the main problem in patient-friendly language."""
    hide_sidebar()
    st.title("Cuéntenos su problema")

    selected_category = st.session_state.get("selected_initial_category", "")
    duration_options = [
        "Menos de 1 semana",
        "Menos de 1 mes",
        "Más de 3 meses",
        "Más de 1 año",
    ]
    saved_problem_details = st.session_state.get("guided_problem_details", {})
    category_fields = {
        "Insomnio": {
            "label": "¿Qué problema tiene con el sueño?",
            "options": [
                "Me cuesta dormir",
                "Me despierto varias veces",
                "Me despierto muy temprano",
                "Duermo pero no descanso",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Estrés o ansiedad": {
            "label": "¿Qué siente principalmente?",
            "options": [
                "Nerviosismo",
                "Preocupación excesiva",
                "Palpitaciones o tensión",
                "Ataques de ansiedad",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Tristeza o depresión": {
            "label": "¿Qué siente principalmente?",
            "options": [
                "Tristeza",
                "Falta de ganas",
                "Cansancio emocional",
                "Pérdida de interés",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Respiración": {
            "label": "¿Cuál es el problema principal?",
            "options": [
                "Falta de aire",
                "Tos",
                "Alergia respiratoria",
                "Asma",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Digestión": {
            "label": "¿Cuál es el problema principal?",
            "options": [
                "Acidez o reflujo",
                "Distensión abdominal",
                "Estreñimiento",
                "Diarrea",
                "Náuseas",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
        "Salud urinaria, próstata o ginecológica": {
            "label": "¿Cuál es el problema principal?",
            "options": [
                "Orinar frecuentemente",
                "Ardor al orinar",
                "Dolor pélvico",
                "Síntomas prostáticos",
                "Síntomas ginecológicos",
                "Otro",
            ],
            "slider_label": "¿Cuánto afecta su vida diaria?",
            "caption": "0 = nada, 10 = muchísimo.",
        },
    }

    other_problem_detail = ""
    if selected_category == "Otro problema de salud":
        problem = st.session_state.get("other_health_problem_description", "")
        st.write(f"**Problema o síntoma principal:** {problem}")
        slider_label = "¿Cuánto afecta su vida diaria?"
        caption = "0 = nada, 10 = muchísimo."
    elif selected_category == "Dolor y movilidad":
        problem = st.text_input(
            "¿Cuál es el problema que desea tratar?",
            value=saved_problem_details.get("problem", ""),
            placeholder="Ejemplo: dolor lumbar, dolor de rodilla, dolor cervical.",
        )
        slider_label = "¿Qué intensidad tiene hoy?"
        caption = "0 = nada, 10 = máximo."
    else:
        field_config = category_fields.get(selected_category, {})
        problem_options = field_config.get("options", ["Otro"])
        saved_problem = saved_problem_details.get("problem")
        problem = st.selectbox(
            field_config.get("label", "¿Cuál es el problema principal?"),
            problem_options,
            index=option_index(
                problem_options,
                saved_problem
                if saved_problem in problem_options
                else "Otro" if saved_problem else None,
            ),
            placeholder="Seleccione una opción",
        )
        if problem == "Otro":
            other_problem_detail = st.text_area(
                "Por favor describa brevemente el problema principal",
                value=(
                    saved_problem
                    if isinstance(saved_problem, str)
                    and saved_problem not in problem_options
                    else ""
                ),
                max_chars=500,
            )
            show_dictation_help()
        slider_label = field_config.get(
            "slider_label",
            "¿Cuánto afecta su vida diaria?",
        )
        caption = field_config.get("caption", "0 = nada, 10 = muchísimo.")

    duration = st.selectbox(
        "¿Hace cuánto tiempo lo tiene?",
        duration_options,
        index=option_index(duration_options, saved_problem_details.get("duration")),
        placeholder="Seleccione una opción",
    )
    intensity = st.slider(
        slider_label,
        min_value=0,
        max_value=10,
        value=int(saved_problem_details.get("intensity", 0)),
        help=caption,
    )
    st.caption(caption)

    def continue_from_problem_details() -> bool:
        problem_text = problem.strip() if isinstance(problem, str) else problem
        if problem == "Otro":
            if not other_problem_detail.strip():
                st.error("Por favor complete este campo para continuar.")
                return False
            problem_text = other_problem_detail.strip()
        if not problem_text or not duration:
            st.error("Complete el problema y el tiempo de evolución.")
            return False
        st.session_state["guided_problem_details"] = {
            "problem": problem_text,
            "duration": duration,
            "intensity": int(intensity),
        }
        return True

    render_patient_navigation(
        "personal_data",
        on_next=continue_from_problem_details,
        next_step="follow_up_orientation",
    )


def render_follow_up_orientation_step() -> None:
    """Collect simple context to orient the patient follow-up."""
    hide_sidebar()
    st.title("Para orientar mejor el seguimiento")
    saved_follow_up = st.session_state.get("guided_follow_up_orientation", {})

    worsens_with = st.text_input(
        "¿Qué empeora su problema?",
        value=saved_follow_up.get("worsens_with", "").replace(
            "Sin completar",
            "",
        ),
        placeholder="Ejemplo: caminar, estrés, comida, frío, noche, esfuerzo.",
    )
    improves_with = st.text_input(
        "¿Qué mejora su problema?",
        value=saved_follow_up.get("improves_with", "").replace(
            "Sin completar",
            "",
        ),
        placeholder="Ejemplo: reposo, calor, medicación, masajes, dormir.",
    )
    medication_options = ["No", "Sí", "No estoy seguro/a"]
    saved_medication = saved_follow_up.get("medication_related")
    saved_medication_option = (
        saved_medication
        if saved_medication in medication_options
        else "Sí" if saved_medication else None
    )
    medication_related = st.radio(
        "¿Toma actualmente algún medicamento relacionado con este problema?",
        medication_options,
        index=option_index(medication_options, saved_medication_option),
    )
    medication_name = ""
    if medication_related == "Sí":
        medication_name = st.text_input(
            "¿Cuál?",
            value=(
                saved_medication
                if saved_medication not in medication_options
                else ""
            ),
        )
    limitation_options = ["No", "Un poco", "Bastante", "Mucho"]
    daily_limitation = st.radio(
        "¿Este problema limita sus actividades diarias?",
        limitation_options,
        index=option_index(
            limitation_options,
            saved_follow_up.get("daily_limitation"),
        ),
    )

    def continue_from_follow_up() -> bool:
        if not medication_related or not daily_limitation:
            st.error("Complete las opciones para continuar.")
            return False
        if medication_related == "Sí" and not medication_name.strip():
            st.error("Indique cuál medicamento toma.")
            return False

        medication_summary = medication_related
        if medication_related == "Sí":
            medication_summary = medication_name.strip()

        st.session_state["guided_follow_up_orientation"] = {
            "worsens_with": worsens_with.strip() or "Sin completar",
            "improves_with": improves_with.strip() or "Sin completar",
            "medication_related": medication_summary,
            "daily_limitation": daily_limitation,
        }
        return True

    next_step = (
        "global_functional_score"
        if st.session_state.get("selected_initial_category") == "Otro problema de salud"
        else "adaptive_details"
    )
    render_patient_navigation(
        "problem_details",
        on_next=continue_from_follow_up,
        next_step=next_step,
    )


def render_adaptive_details_step() -> None:
    """Collect a few patient-friendly details for the selected main reason."""
    hide_sidebar()
    st.title("Un poco más de detalle")

    selected_category = st.session_state.get("selected_initial_category", "")
    adaptive_questions = {
        "Dolor y movilidad": [
            (
                "problem_location",
                "¿Dónde se localiza principalmente el problema?",
                [
                    "Cuello",
                    "Hombro",
                    "Codo",
                    "Mano o muñeca",
                    "Espalda alta",
                    "Espalda baja",
                    "Cadera",
                    "Rodilla",
                    "Tobillo o pie",
                    "Varias zonas",
                    "Otro",
                ],
            ),
            (
                "pain_spread",
                "¿El dolor se extiende hacia otra zona?",
                ["No", "Sí"],
            ),
            (
                "pain_description",
                "¿Qué describe mejor el dolor?",
                [
                    "Punzante",
                    "Ardor",
                    "Rigidez",
                    "Presión",
                    "Hormigueo",
                    "Otro",
                ],
            ),
        ],
        "Insomnio": [
            (
                "sleep_problem",
                "¿Qué ocurre principalmente?",
                [
                    "Me cuesta dormirme",
                    "Me despierto muchas veces",
                    "Me despierto demasiado temprano",
                    "Duermo pero no descanso",
                ],
            ),
            (
                "sleep_hours",
                "¿Cuántas horas duerme aproximadamente?",
                ["Menos de 4", "4 a 5", "6 a 7", "Más de 7"],
            ),
        ],
        "Estrés o ansiedad": [
            (
                "main_stressor",
                "¿Qué lo afecta más?",
                ["Trabajo", "Familia", "Economía", "Salud", "Otro"],
            ),
            (
                "physical_symptoms",
                "¿Tiene síntomas físicos?",
                [
                    "Palpitaciones",
                    "Tensión muscular",
                    "Falta de aire",
                    "Problemas digestivos",
                    "Ninguno",
                    "Otro",
                ],
            ),
        ],
        "Tristeza o depresión": [
            (
                "mood_description",
                "¿Qué describe mejor la situación?",
                [
                    "Tristeza persistente",
                    "Falta de motivación",
                    "Aislamiento",
                    "Cansancio emocional",
                    "Llanto frecuente",
                ],
            ),
        ],
        "Digestión": [
            (
                "digestive_symptom",
                "¿Cuál es el síntoma principal?",
                [
                    "Distensión abdominal",
                    "Acidez",
                    "Reflujo",
                    "Diarrea",
                    "Constipación",
                    "Dolor abdominal",
                ],
            ),
        ],
        "Respiración": [
            (
                "breathing_problem",
                "¿Qué problema presenta?",
                ["Tos", "Falta de aire", "Congestión nasal", "Rinitis", "Otro"],
            ),
        ],
        "Salud urinaria, próstata o ginecológica": [
            (
                "urinary_or_intimate_reason",
                "¿Cuál es el principal motivo?",
                ["Urinario", "Prostático", "Ginecológico", "Sexual", "Otro"],
            ),
        ],
    }
    questions = adaptive_questions.get(selected_category, [])
    if not questions:
        st.session_state["guided_step"] = "global_functional_score"
        st.rerun()

    saved_adaptive_details = st.session_state.get("guided_adaptive_details", {})
    answers = {}
    for key, question, options in questions:
        saved_item = saved_adaptive_details.get(key, {})
        saved_answer = saved_item.get("answer")
        saved_detail_text = (
            saved_answer
            if isinstance(saved_answer, str) and saved_answer not in options
            else ""
        )
        display_answer = saved_answer
        if "Otro" in options and saved_answer not in (None, *options):
            display_answer = "Otro"
        if key == "pain_spread" and saved_answer not in (None, *options):
            display_answer = "Sí"
        answer = st.radio(
            question,
            options,
            index=option_index(options, display_answer),
        )
        other_answer = ""
        requires_detail = False
        if answer == "Otro":
            requires_detail = True
            labels = {
                "problem_location": (
                    "Describa brevemente en qué zona o parte del cuerpo se "
                    "localiza"
                ),
                "pain_description": "Describa brevemente cómo siente el dolor",
                "main_stressor": (
                    "Por favor describa brevemente qué situación considera "
                    "que más influye en su problema actual"
                ),
                "physical_symptoms": (
                    "Describa brevemente los síntomas físicos más importantes"
                ),
                "breathing_problem": (
                    "Describa brevemente el problema respiratorio"
                ),
                "urinary_or_intimate_reason": (
                    "Describa brevemente el motivo principal"
                ),
            }
            other_answer = st.text_area(
                labels.get(key, "Por favor describa brevemente"),
                value=saved_detail_text,
                max_chars=500,
            )
            show_dictation_help()
        elif key == "pain_spread" and answer == "Sí":
            requires_detail = True
            other_answer = st.text_area(
                "Describa hacia dónde se extiende",
                value=saved_detail_text,
                max_chars=500,
            )
            show_dictation_help()
        answers[key] = {
            "question": question,
            "answer": answer,
            "other_answer": other_answer,
            "requires_detail": requires_detail,
        }

    def continue_from_adaptive_details() -> bool:
        if any(not item["answer"] for item in answers.values()):
            st.error("Complete las opciones para continuar.")
            return False
        if any(
            item["requires_detail"] and not item["other_answer"].strip()
            for item in answers.values()
        ):
            st.error("Por favor complete este campo para continuar.")
            return False
        saved_answers = {}
        for key, item in answers.items():
            saved_item = {
                "question": item["question"],
                "answer": item["answer"],
            }
            if item["requires_detail"]:
                saved_item["answer"] = item["other_answer"].strip()
            saved_answers[key] = saved_item
        st.session_state["guided_adaptive_details"] = saved_answers
        return True

    render_patient_navigation(
        "follow_up_orientation",
        on_next=continue_from_adaptive_details,
        next_step="global_functional_score",
    )


def render_global_functional_score_step() -> None:
    """Collect the patient's overall self-reported state for the last week."""
    hide_sidebar()
    st.title("Escala funcional global")
    st.write(
        "Pensando en su vida diaria durante los últimos 7 días, "
        "¿cómo se ha sentido en general?"
    )
    st.caption(
        "Considere su dolor, energía, sueño, estado de ánimo y capacidad para "
        "realizar sus actividades habituales."
    )

    global_functional_score = st.slider(
        "Estado general durante los últimos 7 días",
        min_value=0,
        max_value=10,
        value=int(st.session_state.get("global_functional_score", 5)),
        step=1,
    )
    st.caption("0 = Muy mal · 5 = Regular · 10 = Muy bien")

    def continue_from_global_functional_score() -> bool:
        st.session_state["global_functional_score"] = global_functional_score
        return True

    previous_step = (
        "follow_up_orientation"
        if st.session_state.get("selected_initial_category") == "Otro problema de salud"
        else "adaptive_details"
    )
    render_patient_navigation(
        previous_step,
        on_next=continue_from_global_functional_score,
        next_step="treatment_expectations",
    )


def render_treatment_expectations_step() -> None:
    """Collect the patient's expectations for acupuncture treatment."""
    hide_sidebar()
    st.title("¿Qué espera lograr con el tratamiento de Acupuntura?")
    st.write(
        "No existe una respuesta correcta o incorrecta. Queremos conocer cuál "
        "es el resultado más importante para usted."
    )

    expectation_options = [
        "Reducir el dolor",
        "Eliminar completamente el dolor",
        "Dormir mejor",
        "Reducir el estrés o la ansiedad",
        "Mejorar el estado de ánimo",
        "Mejorar mi movilidad",
        "Mejorar mi calidad de vida",
        "Tener más energía",
        "Reducir medicamentos",
        "Suspender medicamentos, si fuera posible",
        "Evitar una cirugía",
        "Recuperar una actividad que hoy no puedo realizar",
        "Mejorar mi rendimiento físico o deportivo",
        "Mejorar una función específica de mi organismo",
        "Otro objetivo",
    ]
    saved_treatment_expectations = st.session_state.get(
        "guided_treatment_expectations",
        {},
    )
    saved_expectations = saved_treatment_expectations.get("expectations", [])
    saved_other_expectation = next(
        (
            expectation
            for expectation in saved_expectations
            if expectation not in expectation_options
        ),
        "",
    )

    st.write("Seleccione todas las opciones que correspondan")
    selected_expectations = []
    selected_count = sum(
        1
        for index in range(len(expectation_options))
        if st.session_state.get(f"treatment_expectation_option_{index}")
    )
    for index, expectation in enumerate(expectation_options):
        option_key = f"treatment_expectation_option_{index}"
        checked = st.checkbox(
            expectation,
            key=option_key,
            disabled=(
                selected_count >= 2
                and not st.session_state.get(option_key, False)
            ),
        )
        if checked:
            selected_expectations.append(expectation)
    if selected_count >= 2:
        st.info(
            "Para enfocar mejor el seguimiento, registre sus objetivos "
            "principales. Si desea agregar algo más, puede escribirlo en el "
            "espacio libre."
        )
    other_expectation = ""
    if "Otro objetivo" in selected_expectations:
        other_expectation = st.text_area(
            "Describa brevemente cuál sería el resultado ideal para usted",
            value=saved_other_expectation,
            max_chars=500,
        )
        show_dictation_help()
    daily_life_result = st.text_area(
        "Si el tratamiento fuera exitoso, dentro de 3 a 6 meses, ¿qué sería "
        "diferente en su vida cotidiana?",
        value=saved_treatment_expectations.get("daily_life_result", ""),
        max_chars=800,
    )
    show_dictation_help()

    def continue_from_treatment_expectations() -> bool:
        if not selected_expectations or not daily_life_result.strip():
            st.error("Complete las opciones para continuar.")
            return False
        if "Otro objetivo" in selected_expectations and not other_expectation.strip():
            st.error("Por favor complete este campo para continuar.")
            return False
        expectation_summary = [
            expectation
            for expectation in selected_expectations
            if expectation != "Otro objetivo"
        ]
        if "Otro objetivo" in selected_expectations:
            expectation_summary.append(other_expectation.strip())

        st.session_state["guided_treatment_expectations"] = {
            "expectations": expectation_summary,
            "daily_life_result": daily_life_result.strip(),
        }
        return True

    render_patient_navigation(
        "global_functional_score",
        on_next=continue_from_treatment_expectations,
        next_step="thanks",
    )


def render_final_closure_step() -> None:
    """Render the final professional closure after the guided flow is finished."""
    hide_sidebar()
    st.title("EVALUACIÓN COMPLETADA CON ÉXITO")
    st.write(
        "Gracias por dedicar unos minutos a responder.\n\n"
        "La información será revisada por el Dr. Mauricio Uehara y contribuirá "
        "a orientar su estrategia terapéutica.\n\n"
        "Lo esperamos en su consulta para comenzar el tratamiento.\n\n"
        "Hasta pronto."
    )


def render_thanks_step() -> None:
    """Render the patient-friendly summary before the final closure."""
    hide_sidebar()

    personal_data = st.session_state.get("guided_personal_data", {})
    problem_details = st.session_state.get("guided_problem_details", {})
    follow_up_orientation = st.session_state.get(
        "guided_follow_up_orientation",
        {},
    )
    adaptive_details = st.session_state.get("guided_adaptive_details", {})
    treatment_expectations = st.session_state.get(
        "guided_treatment_expectations",
        {},
    )
    st.title("RESUMEN")
    st.write(
        "Revise la información cargada. Si necesita corregir algo, presione "
        "Atrás."
    )
    consultation_type = st.session_state.get(
        "tipo_consulta",
        "Paciente nuevo",
    )
    st.write(f"**Tipo de consulta:** {consultation_type}")
    st.write(
        f"**Motivo principal:** "
        f"{st.session_state.get('selected_initial_category', 'Sin completar')}"
    )
    st.write(f"**Nombre:** {personal_data.get('name', 'Sin completar')}")
    st.write(
        f"**DNI:** "
        f"{'registrado' if personal_data.get('dni') else 'no registrado'}"
    )
    st.write(
        f"**Contacto:** "
        f"{'registrado' if personal_data.get('phone') else 'no registrado'}"
    )
    st.write(
        f"**E-mail:** "
        f"{'registrado' if personal_data.get('email') else 'no registrado'}"
    )
    st.write(
        f"**Problema o síntoma principal:** "
        f"{problem_details.get('problem', 'Sin completar')}"
    )
    st.write(
        f"**Tiempo de evolución:** "
        f"{problem_details.get('duration', 'Sin completar')}"
    )
    intensity = problem_details.get("intensity", "Sin completar")
    st.write(f"**Impacto actual:** {intensity} de 10")
    st.write(
        f"**Empeora con:** "
        f"{follow_up_orientation.get('worsens_with', 'Sin completar')}"
    )
    st.write(
        f"**Mejora con:** "
        f"{follow_up_orientation.get('improves_with', 'Sin completar')}"
    )
    st.write(
        f"**Medicación relacionada:** "
        f"{follow_up_orientation.get('medication_related', 'Sin completar')}"
    )
    st.write(
        f"**Limitación diaria:** "
        f"{follow_up_orientation.get('daily_limitation', 'Sin completar')}"
    )
    for item in adaptive_details.values():
        st.write(f"**{item['question']}** {item['answer']}")
    global_functional_score = st.session_state.get(
        "global_functional_score",
        "Sin completar",
    )
    st.write(
        f"**Estado general últimos 7 días:** {global_functional_score}/10"
    )
    expectations = treatment_expectations.get("expectations", [])
    expectations_text = (
        ", ".join(expectations)
        if expectations
        else "Sin completar"
    )
    st.write(f"**Objetivos principales seleccionados:** {expectations_text}")
    st.write(
        f"**Expectativa expresada libremente:** "
        f"{treatment_expectations.get('daily_life_result', 'Sin completar')}"
    )

    def finish_guided_flow() -> bool:
        store_completed_guided_evaluation()
        st.session_state["guided_step"] = "final_closure"
        return True

    render_patient_navigation(
        "treatment_expectations",
        next_label="Finalizar",
        on_next=finish_guided_flow,
    )

def patient_options(patients: pd.DataFrame) -> dict[str, int]:
    """Build pseudonymized patient labels mapped to database identifiers."""
    return {
        str(row["patient_code"]): int(row["id"])
        for _, row in patients.iterrows()
    }


def professional_patient_options(patients: pd.DataFrame) -> dict[str, int]:
    """Build professional-only labels with patient name and pseudonymized code."""
    options: dict[str, int] = {}
    for _, row in patients.iterrows():
        patient_name = str(row.get("name") or "").strip() or "Sin nombre"
        patient_code = str(row["patient_code"])
        options[f"{patient_name} ({patient_code})"] = int(row["id"])
    return options


def count_values_table(
    evaluations: list[dict],
    field: str,
    labels: list[str] | None = None,
) -> pd.DataFrame:
    """Build a count table while retaining requested zero-count categories."""
    values = [evaluation.get(field) for evaluation in evaluations]
    if labels is None:
        labels = sorted(
            {
                value
                for value in values
                if value not in (None, "", "Sin completar")
            }
        )
    return pd.DataFrame(
        [{field: label, "Cantidad": values.count(label)} for label in labels]
    )


def render_patient_followup_panel_section() -> None:
    """Show session history and evolution charts using existing session data."""
    st.subheader("Historial por paciente")
    patients = get_patients()
    if patients.empty:
        st.info("Todavía no hay pacientes registrados.")
        return

    options = professional_patient_options(patients)
    selected_label = st.selectbox(
        "Seleccionar paciente",
        list(options.keys()),
        key="professional_session_history_patient",
    )
    patient_id = options[selected_label]
    sessions = get_patient_sessions(patient_id)
    if sessions.empty:
        st.info("El paciente seleccionado todavía no tiene sesiones registradas.")
        return

    table_data = format_sessions_for_followup(sessions)
    st.dataframe(table_data, hide_index=True, use_container_width=True)

    chart_data = sessions.copy().sort_values("session_number")
    intensity_figure = px.line(
        chart_data,
        x="session_number",
        y="eva_pre",
        markers=True,
        title="Intensidad por sesión",
        labels={"session_number": "Sesión", "eva_pre": "Intensidad actual"},
    )
    intensity_figure.update_yaxes(range=[0, 10], dtick=1)
    st.plotly_chart(intensity_figure, use_container_width=True)

    global_figure = px.line(
        chart_data,
        x="session_number",
        y="functional_impact",
        markers=True,
        title="Estado general por sesión",
        labels={
            "session_number": "Sesión",
            "functional_impact": "Estado general últimos 7 días",
        },
    )
    global_figure.update_yaxes(range=[0, 10], dtick=1)
    st.plotly_chart(global_figure, use_container_width=True)
    st.caption(
        "El panel utiliza nombre y código interno. No muestra DNI, teléfono "
        "ni correo electrónico completos."
    )


def render_therapeutic_cycles_panel_section() -> None:
    """Show therapeutic cycles and their follow-up counts for professionals."""
    st.subheader("Ciclos terapéuticos por paciente")
    ensure_therapeutic_cycles_schema()
    patients = get_patients()
    if patients.empty:
        st.info("Todavía no hay pacientes registrados.")
        return

    patient_options_by_label = professional_patient_options(patients)
    selected_patient_label = st.selectbox(
        "Ver paciente",
        list(patient_options_by_label.keys()),
        key="professional_cycles_patient",
    )
    selected_patient_id = patient_options_by_label[selected_patient_label]

    with sqlite3.connect(database_module.DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        cycle_rows = connection.execute(
            """
            SELECT
                cycle.id,
                cycle.patient_id,
                cycle.fecha_inicio,
                cycle.tipo_consulta,
                cycle.main_reason,
                cycle.main_problem,
                cycle.status,
                COUNT(session.id) AS session_count
            FROM therapeutic_cycles AS cycle
            LEFT JOIN sessions AS session
                ON session.therapeutic_cycle_id = cycle.id
            WHERE cycle.patient_id = ?
            GROUP BY cycle.id
            ORDER BY cycle.fecha_inicio DESC, cycle.id DESC
            """,
            (selected_patient_id,),
        ).fetchall()

    if not cycle_rows:
        st.info("Este paciente todavía no tiene ciclos terapéuticos registrados.")
        return

    cycles = [dict(cycle) for cycle in cycle_rows]
    cycle_dates = pd.to_datetime(
        [cycle["fecha_inicio"] for cycle in cycles],
        errors="coerce",
    ).dropna()
    treated_reasons = sorted(
        {
            fix_visible_encoding(cycle["main_reason"] or "Sin completar")
            for cycle in cycles
        }
    )
    active_cycle_count = sum(1 for cycle in cycles if cycle["status"] == "activo")
    closed_cycle_count = sum(1 for cycle in cycles if cycle["status"] == "cerrado")
    total_followups = sum(int(cycle["session_count"]) for cycle in cycles)

    st.markdown("**Resumen global del paciente**")
    metric_columns = st.columns(4)
    metric_columns[0].metric("Ciclos terapéuticos", len(cycles))
    metric_columns[1].metric("Seguimientos totales", total_followups)
    metric_columns[2].metric("Ciclos activos", active_cycle_count)
    metric_columns[3].metric("Ciclos cerrados", closed_cycle_count)
    first_consultation = (
        cycle_dates.min().strftime("%d/%m/%Y") if not cycle_dates.empty else "Sin fecha"
    )
    last_consultation = (
        cycle_dates.max().strftime("%d/%m/%Y") if not cycle_dates.empty else "Sin fecha"
    )
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Primera consulta registrada": first_consultation,
                    "Última consulta registrada": last_consultation,
                    "Motivos tratados": ", ".join(treated_reasons),
                }
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("**Línea de tiempo de ciclos terapéuticos**")
    for cycle in sorted(cycles, key=lambda item: (item["fecha_inicio"], item["id"])):
        cycle_date = pd.to_datetime(cycle["fecha_inicio"], errors="coerce")
        display_date = (
            cycle_date.strftime("%d/%m/%Y")
            if not pd.isna(cycle_date)
            else cycle["fecha_inicio"]
        )
        with st.container(border=True):
            st.write(f"**{display_date}**")
            st.write(f"**Ciclo {int(cycle['id'])}**")
            st.write(
                f"Tipo de consulta: "
                f"{fix_visible_encoding(cycle['tipo_consulta'] or 'Sin completar')}"
            )
            st.write(
                f"Motivo: "
                f"{fix_visible_encoding(cycle['main_reason'] or 'Sin completar')}"
            )
            st.write(
                f"Problema: "
                f"{fix_visible_encoding(cycle['main_problem'] or 'Sin completar')}"
            )
            st.write(f"Seguimientos: {int(cycle['session_count'])}")
            st.write(f"Estado: {cycle['status']}")

    summary_rows = [
        {
            "Ciclo ID": int(cycle["id"]),
            "Fecha de inicio": cycle["fecha_inicio"],
            "Tipo de consulta": fix_visible_encoding(
                cycle["tipo_consulta"] or "Sin completar"
            ),
            "Motivo principal": fix_visible_encoding(
                cycle["main_reason"] or "Sin completar"
            ),
            "Problema principal": fix_visible_encoding(
                cycle["main_problem"] or "Sin completar"
            ),
            "Estado del ciclo": cycle["status"],
            "Cantidad de seguimientos": int(cycle["session_count"]),
        }
        for cycle in cycles
    ]
    st.dataframe(
        pd.DataFrame(summary_rows),
        hide_index=True,
        use_container_width=True,
    )

    cycle_options = {cycle_label(cycle): int(cycle["id"]) for cycle in cycles}
    selected_cycle_label = st.selectbox(
        "Ver evolución de ciclo",
        list(cycle_options.keys()),
        key="professional_cycle_detail",
    )
    selected_cycle_id = cycle_options[selected_cycle_label]
    selected_cycle = next(
        cycle for cycle in cycles if int(cycle["id"]) == selected_cycle_id
    )
    if selected_cycle["status"] == "activo":
        if st.button("Cerrar ciclo seleccionado (alta)", use_container_width=True):
            close_therapeutic_cycle(selected_cycle_id)
            st.success("Ciclo terapéutico cerrado.")
            st.rerun()
    sessions = get_cycle_sessions(selected_cycle_id)
    if sessions.empty:
        st.info("Este ciclo todavía no tiene seguimientos registrados.")
    else:
        st.dataframe(
            format_sessions_for_followup(sessions),
            hide_index=True,
            use_container_width=True,
        )
        chart_data = sessions.copy().sort_values("session_number")
        intensity_figure = px.line(
            chart_data,
            x="session_number",
            y="eva_pre",
            markers=True,
            title="Intensidad actual por sesión",
            labels={"session_number": "Sesión", "eva_pre": "Intensidad actual"},
        )
        intensity_figure.update_yaxes(range=[0, 10], dtick=1)
        st.plotly_chart(intensity_figure, use_container_width=True)

        global_figure = px.line(
            chart_data,
            x="session_number",
            y="functional_impact",
            markers=True,
            title="Estado general por sesión",
            labels={
                "session_number": "Sesión",
                "functional_impact": "Estado general últimos 7 días",
            },
        )
        global_figure.update_yaxes(range=[0, 10], dtick=1)
        st.plotly_chart(global_figure, use_container_width=True)

        comments = [
            fix_visible_encoding(str(comment).strip())
            for comment in sessions.get("notes", pd.Series(dtype=str)).fillna("")
            if str(comment).strip()
        ]
        st.markdown("**Comentarios registrados**")
        if comments:
            for comment in comments:
                st.write(comment)
        else:
            st.info("No hay comentarios registrados para este ciclo.")


def render_professional_panel() -> None:
    """Render the persistent professional overview of completed evaluations."""
    hide_sidebar()
    if st.button("Volver al inicio"):
        st.session_state["guided_step"] = "welcome"
        st.rerun()

    st.title("Panel profesional")
    st.subheader("Dr. Mauricio Uehara - PROM-ACU")
    render_patient_followup_panel_section()
    st.divider()
    render_therapeutic_cycles_panel_section()
    st.divider()

    try:
        evaluations = load_completed_guided_evaluations()
    except sqlite3.Error as error:
        st.error(f"No se pudieron recuperar las evaluaciones: {error}")
        return

    if not evaluations:
        st.info("Todavía no hay evaluaciones registradas.")
        return

    evaluations_df = pd.DataFrame(evaluations)
    st.metric("Total de evaluaciones completadas", len(evaluations))

    st.subheader("Motivos principales más frecuentes")
    reasons_table = count_values_table(evaluations, "Motivo principal")
    if reasons_table.empty:
        st.info("Sin datos de motivo principal.")
    else:
        reasons_table = reasons_table.sort_values(
            ["Cantidad", "Motivo principal"], ascending=[False, True]
        )
        st.dataframe(reasons_table, hide_index=True, use_container_width=True)

    impact_values = pd.to_numeric(
        evaluations_df["Impacto actual"], errors="coerce"
    ).dropna()
    functional_values = pd.to_numeric(
        evaluations_df["Estado general últimos 7 días"], errors="coerce"
    ).dropna()
    impact_average = impact_values.mean() if not impact_values.empty else None
    functional_average = (
        functional_values.mean() if not functional_values.empty else None
    )
    average_columns = st.columns(2)
    average_columns[0].metric(
        "Impacto actual promedio",
        f"{impact_average:.1f} de 10" if impact_average is not None else "Sin datos",
    )
    average_columns[1].metric(
        "Estado general promedio últimos 7 días",
        (
            f"{functional_average:.1f} de 10"
            if functional_average is not None
            else "Sin datos"
        ),
    )

    st.subheader("Tiempo de evolución")
    st.dataframe(
        count_values_table(
            evaluations,
            "Tiempo de evolución",
            [
                "Menos de 1 semana",
                "Menos de 1 mes",
                "Más de 3 meses",
                "Más de 1 año",
            ],
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Limitación diaria")
    st.dataframe(
        count_values_table(
            evaluations,
            "Limitación diaria",
            ["No", "Un poco", "Bastante", "Mucho"],
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Medicación relacionada")
    st.dataframe(
        count_values_table(
            evaluations,
            "Medicación relacionada",
            ["No", "Sí", "No estoy seguro/a"],
        ),
        hide_index=True,
        use_container_width=True,
    )
    medication_names = [
        value
        for value in evaluations_df["Medicamento informado"].dropna().tolist()
        if str(value).strip()
    ]
    if medication_names:
        st.markdown("**Medicamentos informados**")
        for medication_name in medication_names:
            st.write(f"- {medication_name}")

    st.subheader("Expectativas terapéuticas principales")
    expectation_counts: dict[str, int] = {}
    for evaluation in evaluations:
        for objective in evaluation.get("Objetivos principales seleccionados", []):
            expectation_counts[objective] = expectation_counts.get(objective, 0) + 1
    expectations_table = pd.DataFrame(
        [
            {"Objetivo": objective, "Cantidad": count}
            for objective, count in sorted(
                expectation_counts.items(), key=lambda item: (-item[1], item[0])
            )
        ],
        columns=["Objetivo", "Cantidad"],
    )
    if expectations_table.empty:
        st.info("Sin datos de objetivos terapéuticos.")
    else:
        st.dataframe(expectations_table, hide_index=True, use_container_width=True)

    st.subheader("Listado de evaluaciones")
    display_df = evaluations_df.copy()
    display_df["Objetivos principales seleccionados"] = display_df[
        "Objetivos principales seleccionados"
    ].apply(lambda values: ", ".join(values) if values else "Sin completar")
    list_columns = [
        "Fecha/hora",
        "Nombre",
        "DNI",
        "Contacto",
        "Tipo de consulta",
        "Motivo principal",
        "Problema o síntoma principal",
        "Tiempo de evolución",
        "Impacto actual",
        "Estado general últimos 7 días",
        "Limitación diaria",
        "Medicación relacionada",
        "Objetivos principales seleccionados",
    ]
    st.dataframe(
        display_df[list_columns],
        hide_index=True,
        use_container_width=True,
    )

    csv_columns = [
        "Evaluación ID",
        "Fecha/hora",
        "Tipo de consulta",
        "Motivo principal",
        "Problema o síntoma principal",
        "Tiempo de evolución",
        "Impacto actual",
        "Estado general últimos 7 días",
        "Limitación diaria",
        "Medicación relacionada",
        "Medicamento informado",
        "Objetivos principales seleccionados",
    ]
    pseudonymized_csv = display_df[csv_columns].to_csv(index=False)
    st.download_button(
        "Descargar CSV seudonimizado",
        data=pseudonymized_csv.encode("utf-8-sig"),
        file_name="prom_acu_evaluaciones_seudonimizadas.csv",
        mime="text/csv",
        type="primary",
    )
    st.caption(
        "La descarga no incluye nombre, DNI, teléfono ni correo electrónico."
    )

def render_home() -> None:
    st.title("PROM-ACU")
    st.subheader("Seguimiento clínico de pacientes tratados con acupuntura")
    show_medical_warning()
    st.markdown(
        """
        Esta demo permite registrar pacientes y sesiones, seguir la evolución
        del dolor mediante EVA, visualizar tendencias y generar un informe
        clínico descriptivo.

        **Alcance del MVP**

        - Registro local y privado en SQLite.
        - Clasificación clínica por categoría y subcategoría.
        - PROM específico sugerido, todavía no administrado.
        - EVA antes y después de cada sesión.
        - Impacto funcional global de 0 a 10.
        - Medicación relevante y evolución del consumo de analgésicos.
        - Severidad de eventos adversos.
        - Cálculo de mejoría absoluta y porcentual.
        - Dashboard y gráfico de evolución.
        - Informe clínico descargable en texto.
        """
    )
    st.info(
        "WOMAC está disponible en Fase 1 como carga resumida. Los demás PROMs "
        "específicos permanecen pendientes de implementación."
    )


def render_patient_registration() -> None:
    st.header("Nuevo paciente")
    show_medical_warning()

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nombre y apellido *", max_chars=120)
        dni = st.text_input("DNI *", max_chars=30)
        age = st.number_input("Edad *", min_value=0, max_value=120, value=18)
        sex = st.selectbox(
            "Sexo *",
            ["Femenino", "Masculino", "Intersexual", "Otro", "Prefiere no informar"],
        )
        phone = st.text_input("Teléfono", max_chars=40)
        care_origin = st.selectbox(
            "Origen asistencial *",
            ["Hospital Avellaneda", "Consultorio Privado"],
            index=None,
            placeholder="Seleccione el origen asistencial",
        )
    with col2:
        diagnosis = st.text_input(
            "Diagnóstico médico principal *",
            max_chars=200,
            help="Registrar únicamente el diagnóstico médico ya existente.",
        )
        category = st.selectbox(
            "Categoría clínica *",
            options=list(CLINICAL_CLASSIFICATION.keys()),
            index=None,
            placeholder="Seleccione una categoría",
        )
        subcategory_options = (
            list(CLINICAL_CLASSIFICATION[category].keys()) if category else []
        )
        subcategory = st.selectbox(
            "Subcategoría *",
            options=subcategory_options,
            index=None,
            placeholder=(
                "Seleccione una subcategoría"
                if category
                else "Primero seleccione una categoría"
            ),
            disabled=category is None,
        )
        suggested_prom = (
            get_suggested_prom(category, subcategory)
            if category and subcategory
            else ""
        )
        st.text_input(
            "PROM sugerido",
            value=suggested_prom,
            disabled=True,
            placeholder="Se asignará según la subcategoría",
        )
        st.caption(
            f"Estado: {get_prom_implementation_status(suggested_prom)} "
            "La clasificación organiza el seguimiento y no constituye un "
            "diagnóstico automático."
        )

    submitted = st.button(
        "Registrar paciente",
        type="primary",
        use_container_width=True,
    )
    if submitted:
        if (
            not name.strip()
            or not dni.strip()
            or not diagnosis.strip()
            or not category
            or not subcategory
            or not care_origin
        ):
            st.error("Complete todos los campos obligatorios marcados con *.")
            return
        if dni_exists(dni):
            st.error("Ya existe un paciente registrado con ese DNI.")
            return

        try:
            patient_id = add_patient(
                name=name,
                dni=dni,
                age=int(age),
                sex=sex,
                phone=phone,
                diagnosis=diagnosis,
                main_complaint=subcategory,
                assigned_scale=suggested_prom,
                clinical_category=category,
                clinical_subcategory=subcategory,
                suggested_prom=suggested_prom,
                care_origin=care_origin,
            )
            create_therapeutic_cycle(
                patient_id=patient_id,
                consultation_type="Consulta inicial actual",
                main_reason=category,
                main_problem=subcategory,
            )
            patient = get_patient(patient_id)
            patient_code = patient["patient_code"] if patient else "No disponible"
            st.success(
                f"Paciente registrado correctamente. Código único: {patient_code}"
            )
        except sqlite3.IntegrityError:
            st.error("No se pudo registrar: revise el DNI y los datos ingresados.")
        except sqlite3.Error as error:
            st.error(f"Error de base de datos: {error}")


def render_session_registration() -> None:
    st.header("Seguimiento del paciente")
    show_medical_warning()
    patients = get_patients()

    if patients.empty:
        st.info("Primero registre al menos un paciente.")
        return

    options = patient_options(patients)
    selected_label = st.selectbox("Seleccionar paciente", list(options.keys()))
    patient_id = options[selected_label]
    patient = get_patient(patient_id)
    active_cycles = get_patient_cycles(patient_id, active_only=True)
    if not active_cycles and patient:
        create_therapeutic_cycle(
            patient_id=patient_id,
            consultation_type="Consulta inicial actual",
            main_reason=patient["clinical_category"] or patient["diagnosis"],
            main_problem=patient["main_complaint"],
        )
        active_cycles = get_patient_cycles(patient_id, active_only=True)
    selected_cycle_label = st.selectbox(
        "Ciclo terapéutico activo",
        [cycle_label(cycle) for cycle in active_cycles],
        key="professional_session_cycle",
    )
    selected_cycle = next(
        cycle for cycle in active_cycles if cycle_label(cycle) == selected_cycle_label
    )
    existing_sessions = get_patient_sessions(patient_id)
    suggested_number = (
        int(existing_sessions["session_number"].max()) + 1
        if not existing_sessions.empty
        else 1
    )

    with st.form("session_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            session_number = st.number_input(
                "Número de sesión *",
                min_value=1,
                value=suggested_number,
                step=1,
            )
            session_date = st.date_input(
                "Fecha *",
                value=date.today(),
                max_value=date.today(),
            )
            eva_pre = st.slider(
                "EVA antes de la sesión",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
            )
            eva_post = st.slider(
                "EVA después de la sesión",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
            )
            pgic = st.selectbox(
                "Comparado con el inicio del tratamiento, ¿cómo se encuentra hoy?",
                options=list(PGIC_OPTIONS.keys()),
                index=None,
                placeholder="Seleccione una opción",
                format_func=lambda value: f"{value}. {PGIC_OPTIONS[value]}",
            )
            functional_impact = st.slider(
                "¿Cuánto afecta actualmente su problema principal a sus "
                "actividades habituales?",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
                help="0: no afecta. 10: impide por completo las actividades.",
            )
        with col2:
            medication_name = st.text_input(
                "Medicación relevante actual",
                max_chars=200,
                placeholder="Nombre del medicamento o 'No usa'",
            )
            medication_frequency = st.text_input(
                "Frecuencia de uso",
                max_chars=120,
                placeholder="Ej.: cada 8 horas, según necesidad",
            )
            analgesic_change = st.selectbox(
                "Consumo de analgésicos comparado con el inicio",
                options=ANALGESIC_CHANGE_OPTIONS,
                index=None,
                placeholder="Seleccione una opción",
            )
            adverse_event_severity = st.selectbox(
                "Eventos adversos",
                options=ADVERSE_EVENT_SEVERITY_OPTIONS,
                index=0,
            )
            adverse_description = st.text_area(
                "Descripción de eventos adversos",
                max_chars=1000,
                help=(
                    "Completar cuando la severidad sea Leve, Moderado o Severo."
                ),
            )
            notes = st.text_area("Observaciones clínicas", max_chars=2000)

        submitted = st.form_submit_button(
            "Guardar sesión",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if pgic is None:
            st.error("Seleccione una opción de PGIC.")
            return
        if analgesic_change is None:
            st.error(
                "Seleccione el consumo de analgésicos comparado con el inicio."
            )
            return
        if (
            adverse_event_severity != "Ninguno"
            and not adverse_description.strip()
        ):
            st.error("Describa el evento adverso registrado.")
            return
        if session_number_exists(patient_id, int(session_number)):
            st.error("Ese número de sesión ya existe para el paciente.")
            return

        try:
            session_id = add_session(
                patient_id=patient_id,
                session_number=int(session_number),
                date=session_date.isoformat(),
                eva_pre=float(eva_pre),
                eva_post=float(eva_post),
                pgic=int(pgic),
                functional_impact=float(functional_impact),
                medication_name=medication_name,
                medication_frequency=medication_frequency,
                analgesic_change=analgesic_change,
                adverse_event_severity=adverse_event_severity,
                adverse_event_description=adverse_description,
                notes=notes,
            )
            assign_session_to_cycle(session_id, int(selected_cycle["id"]))
            st.success("Sesión registrada correctamente.")
        except sqlite3.IntegrityError:
            st.error("No se pudo guardar la sesión. Verifique los datos.")
        except sqlite3.Error as error:
            st.error(f"Error de base de datos: {error}")


def render_womac_assessment() -> None:
    """Render the summarized WOMAC Likert 0-4 assessment."""
    def womac_interpretation(score: int) -> str:
        if score <= 24:
            return "Leve"
        if score <= 48:
            return "Moderada"
        if score <= 72:
            return "Severa"
        return "Muy severa"

    st.header("Evaluación de dolor y movilidad")
    show_medical_warning()
    patients = get_patients()

    if patients.empty:
        st.info("Primero registre al menos un paciente.")
        return

    options = patient_options(patients)
    selected_code = st.selectbox(
        "Código del paciente",
        [""] + list(options.keys()),
        format_func=lambda value: value or "Seleccione un código de paciente",
        key="womac_patient",
    )
    if not selected_code:
        st.info(
            "Seleccione un código de paciente para comenzar la evaluación WOMAC."
        )
        return

    st.success(f"Evaluando paciente: {selected_code}")
    patient_id = options[selected_code]
    patient = get_patient(patient_id)
    assessments = get_patient_womac_assessments(patient_id)

    if patient:
        st.info(
            "**Instrumento recomendado para seguimiento**\n\n"
            "Para este paciente, el instrumento recomendado es WOMAC / KOOS "
            "según categoría clínica y criterio profesional."
        )
        if "WOMAC" not in str(patient.get("suggested_prom") or ""):
            st.warning(
                "WOMAC no figura como PROM sugerido para esta clasificación. "
                "Confirme la pertinencia clínica antes de registrarlo."
            )

    st.markdown(
        "Ingrese el resultado total obtenido en cada dominio del cuestionario "
        "WOMAC ya completado por el paciente.\n\n"
        "- Dolor = suma de 5 preguntas (0–20)\n"
        "- Rigidez = suma de 2 preguntas (0–8)\n"
        "- Función física = suma de 17 preguntas (0–68)\n\n"
        "Esta pantalla no administra los 24 ítems individuales. Solo registra "
        "los resultados resumidos por dominio."
    )

    with st.form("womac_form", clear_on_submit=True):
        assessment_type = st.selectbox(
            "Tipo de evaluación",
            ["Basal", "Seguimiento", "Final"],
        )
        session_number = st.number_input(
            "Número de sesión",
            min_value=1,
            step=1,
            value=1,
        )
        st.info(
            "Número correlativo de la sesión de tratamiento.\n\n"
            "- Basal = sesión inicial.\n"
            "- Seguimiento = sesiones posteriores."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            pain_score = st.number_input(
                "Dolor total (0–20)",
                min_value=0,
                max_value=20,
                step=1,
                value=0,
                help="Suma resumida de dolor: 0 a 20.",
            )
        with col2:
            stiffness_score = st.number_input(
                "Rigidez total (0–8)",
                min_value=0,
                max_value=8,
                step=1,
                value=0,
                help="Suma resumida de rigidez: 0 a 8.",
            )
        with col3:
            function_score = st.number_input(
                "Función física total (0–68)",
                min_value=0,
                max_value=68,
                step=1,
                value=0,
                help="Suma resumida de función física: 0 a 68.",
            )
        total_score = (
            int(pain_score)
            + int(stiffness_score)
            + int(function_score)
        )
        st.markdown(f"**Puntaje WOMAC total: {total_score} / 96**")
        womac_severity = womac_interpretation(total_score)
        st.info(f"**Interpretación clínica: {womac_severity}**")
        submitted = st.form_submit_button(
            "Guardar evaluación",
            type="secondary",
            use_container_width=True,
        )

    if submitted:
        if (
            assessment_type == "Basal"
            and not assessments.empty
            and (assessments["assessment_type"] == "Basal").any()
        ):
            st.error("Este paciente ya tiene una evaluación WOMAC basal.")
            return
        if womac_assessment_exists(patient_id, int(session_number)):
            st.error("Ya existe una evaluación WOMAC para ese número de sesión.")
            return

        try:
            add_womac_assessment(
                patient_id=patient_id,
                assessment_type=assessment_type,
                session_number=int(session_number),
                pain_score=int(pain_score),
                stiffness_score=int(stiffness_score),
                function_score=int(function_score),
            )
            evaluation_label = (
                "basal" if assessment_type == "Basal" else "de seguimiento"
            )
            st.success(
                f"Evaluación {evaluation_label} registrada correctamente.\n\n"
                f"WOMAC total: {total_score}/96 ({womac_severity})\n\n"
                f"Sesión: {int(session_number)}"
            )
        except sqlite3.IntegrityError:
            st.error(
                "No se pudo guardar WOMAC. Revise el número de sesión y "
                "los rangos ingresados."
            )
        except sqlite3.Error as error:
            st.error(f"Error de base de datos: {error}")

    assessments = get_patient_womac_assessments(patient_id)
    if not assessments.empty:
        st.subheader("Historial WOMAC")
        ordered_assessments = assessments.sort_values(
            ["session_number", "id"]
        ).reset_index(drop=True)
        latest_assessment_id = int(ordered_assessments.iloc[-1]["id"])

        headers = st.columns([1.2, 0.7, 0.9, 1.1, 1.1, 1.2, 0.9])
        for column, label in zip(
            headers,
            [
                "Estado",
                "Sesión",
                "Total",
                "Interpretación",
                "Tipo",
                "Registrado",
                "Acciones",
            ],
        ):
            column.markdown(f"**{label}**")

        for _, assessment in ordered_assessments.iterrows():
            assessment_id = int(assessment["id"])
            assessment_type_value = str(assessment["assessment_type"])
            is_latest = assessment_id == latest_assessment_id
            if assessment_type_value == "Basal":
                status_badge = (
                    '<span style="background:#dbeafe;color:#1e40af;'
                    'padding:0.2rem 0.55rem;border-radius:0.75rem;'
                    'font-weight:600;">Inicial</span>'
                )
            elif is_latest:
                status_badge = (
                    '<span style="background:#dcfce7;color:#166534;'
                    'padding:0.2rem 0.55rem;border-radius:0.75rem;'
                    'font-weight:600;">Actual</span>'
                )
            else:
                status_badge = (
                    '<span style="background:#f3f4f6;color:#374151;'
                    'padding:0.2rem 0.55rem;border-radius:0.75rem;'
                    'font-weight:600;">Seguimiento</span>'
                )

            row = st.columns([1.2, 0.7, 0.9, 1.1, 1.1, 1.2, 0.9])
            row[0].markdown(status_badge, unsafe_allow_html=True)
            row[1].write(int(assessment["session_number"]))
            row[2].write(f"{int(assessment['total_score'])}/96")
            row[3].write(
                womac_interpretation(int(assessment["total_score"]))
            )
            row[4].write(assessment_type_value)
            row[5].write(str(assessment["created_at"]))
            if row[6].button(
                "Ver detalle",
                key=f"womac_detail_{assessment_id}",
                use_container_width=True,
            ):
                st.session_state["womac_detail_id"] = assessment_id

        detail_id = st.session_state.get("womac_detail_id")
        detail_rows = ordered_assessments[
            ordered_assessments["id"] == detail_id
        ]
        if not detail_rows.empty:
            detail = detail_rows.iloc[0]
            with st.expander(
                f"Detalle WOMAC · Sesión {int(detail['session_number'])}",
                expanded=True,
            ):
                detail_columns = st.columns(4)
                detail_columns[0].metric(
                    "Dolor", f"{int(detail['pain_score'])}/20"
                )
                detail_columns[1].metric(
                    "Rigidez", f"{int(detail['stiffness_score'])}/8"
                )
                detail_columns[2].metric(
                    "Función física", f"{int(detail['function_score'])}/68"
                )
                detail_columns[3].metric(
                    "WOMAC total", f"{int(detail['total_score'])}/96"
                )
                st.write(
                    "**Interpretación:** "
                    f"{womac_interpretation(int(detail['total_score']))}"
                )

        if len(ordered_assessments) >= 2:
            basal_rows = ordered_assessments[
                ordered_assessments["assessment_type"] == "Basal"
            ]
            if not basal_rows.empty:
                basal = basal_rows.iloc[0]
                current = ordered_assessments.iloc[-1]
                basal_total = int(basal["total_score"])
                current_total = int(current["total_score"])
                score_change = current_total - basal_total
                improvement = (
                    None
                    if basal_total == 0
                    else ((basal_total - current_total) / basal_total) * 100
                )
                if score_change < 0:
                    evolution = "Mejoría clínica"
                elif score_change > 0:
                    evolution = "Empeoramiento"
                else:
                    evolution = "Sin cambios"

                st.subheader("Resumen de evolución")
                summary_columns = st.columns(3)
                summary_columns[0].metric(
                    "WOMAC basal",
                    f"{basal_total}/96",
                    womac_interpretation(basal_total),
                )
                summary_columns[1].metric(
                    "Último WOMAC",
                    f"{current_total}/96",
                    womac_interpretation(current_total),
                )
                summary_columns[2].metric(
                    "Porcentaje de mejoría",
                    (
                        f"{improvement:.1f}%"
                        if improvement is not None
                        else "No calculable"
                    ),
                )
                st.markdown(
                    f"**Cambio absoluto:** {score_change:+d} puntos  \n"
                    f"**Mejoría relativa:** "
                    f"{f'{improvement:.1f}%' if improvement is not None else 'No calculable'}  \n"
                    f"**Evolución:** {evolution}"
                )


def classify_womac_response(
    assessment_count: int,
    baseline_score: float | None,
    latest_score: float | None,
) -> tuple[str, float | None, float | None]:
    """Classify longitudinal WOMAC response for the dashboard."""
    if (
        assessment_count < 2
        or baseline_score is None
        or latest_score is None
        or pd.isna(baseline_score)
        or pd.isna(latest_score)
        or float(baseline_score) == 0
    ):
        return "No comparable", None, None

    baseline = float(baseline_score)
    latest = float(latest_score)
    difference = latest - baseline
    improvement = ((baseline - latest) / baseline) * 100

    if improvement >= 20:
        response = "Respondedor"
    elif improvement >= 10:
        response = "Mejoría parcial"
    elif improvement > -10:
        response = "Sin cambios"
    else:
        response = "Empeorado"

    return response, round(difference, 1), round(improvement, 1)


def build_womac_patient_summary(assessments: pd.DataFrame) -> pd.DataFrame:
    """Build one longitudinal WOMAC summary row per patient."""
    summaries: list[dict[str, object]] = []
    if assessments.empty:
        return pd.DataFrame()

    for (_, patient_code), patient_data in assessments.groupby(
        ["patient_id", "patient_code"],
        sort=False,
    ):
        ordered = patient_data.sort_values(["session_number", "id"])
        baseline_rows = ordered[ordered["assessment_type"] == "Basal"]
        baseline = baseline_rows.iloc[0] if not baseline_rows.empty else None
        latest = ordered.iloc[-1]
        baseline_score = (
            float(baseline["total_score"]) if baseline is not None else None
        )
        latest_score = float(latest["total_score"])
        response, difference, improvement = classify_womac_response(
            len(ordered),
            baseline_score,
            latest_score,
        )
        sessions_between = (
            int(latest["session_number"]) - int(baseline["session_number"])
            if baseline is not None and len(ordered) >= 2
            else None
        )
        summaries.append(
            {
                "patient_code": patient_code,
                "diagnosis": ordered.iloc[0]["diagnosis"],
                "clinical_category": ordered.iloc[0]["clinical_category"],
                "clinical_subcategory": ordered.iloc[0][
                    "clinical_subcategory"
                ],
                "baseline_womac": baseline_score,
                "latest_womac": latest_score,
                "absolute_difference": difference,
                "improvement_percentage": improvement,
                "sessions_between": sessions_between,
                "assessment_count": len(ordered),
                "clinical_response": response,
            }
        )

    return pd.DataFrame(summaries)


def render_womac_dashboard(care_origin: str = "Todos") -> None:
    """Render the read-only WOMAC v1 dashboard."""
    st.divider()
    st.subheader("Dashboard WOMAC")
    assessments = get_womac_dashboard_assessments()
    if care_origin != "Todos":
        assessments = assessments[
            assessments["care_origin"] == care_origin
        ]

    if assessments.empty:
        st.info("Todavía no hay evaluaciones WOMAC para analizar.")
        return

    st.markdown("#### Filtros clínicos")
    filter_columns = st.columns(3)
    diagnosis_options = sorted(
        assessments["diagnosis"].dropna().astype(str).unique().tolist()
    )
    selected_diagnosis = filter_columns[0].selectbox(
        "Diagnóstico",
        ["Todos"] + diagnosis_options,
        key="womac_filter_diagnosis",
    )
    filtered_assessments = assessments.copy()
    if selected_diagnosis != "Todos":
        filtered_assessments = filtered_assessments[
            filtered_assessments["diagnosis"] == selected_diagnosis
        ]

    category_options = sorted(
        filtered_assessments["clinical_category"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    selected_category = filter_columns[1].selectbox(
        "Categoría",
        ["Todas"] + category_options,
        key="womac_filter_category",
    )
    if selected_category != "Todas":
        filtered_assessments = filtered_assessments[
            filtered_assessments["clinical_category"] == selected_category
        ]

    subcategory_options = sorted(
        filtered_assessments["clinical_subcategory"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    selected_subcategory = filter_columns[2].selectbox(
        "Subcategoría",
        ["Todas"] + subcategory_options,
        key="womac_filter_subcategory",
    )
    if selected_subcategory != "Todas":
        filtered_assessments = filtered_assessments[
            filtered_assessments["clinical_subcategory"]
            == selected_subcategory
        ]

    if filtered_assessments.empty:
        st.info("No hay evaluaciones WOMAC para los filtros seleccionados.")
        return

    summary = build_womac_patient_summary(filtered_assessments)
    comparable = summary[
        summary["improvement_percentage"].notna()
    ]
    response_counts = summary["clinical_response"].value_counts()
    average_improvement = (
        comparable["improvement_percentage"].mean()
        if not comparable.empty
        else None
    )
    median_improvement = (
        comparable["improvement_percentage"].median()
        if not comparable.empty
        else None
    )
    improvement_std = (
        comparable["improvement_percentage"].std()
        if len(comparable) >= 2
        else None
    )
    improved_patients = int(
        summary["clinical_response"].isin(
            ["Respondedor", "Mejoría parcial"]
        ).sum()
    )

    metric_row_1 = st.columns(5)
    metric_row_1[0].metric(
        "Pacientes con WOMAC",
        int(summary["patient_code"].nunique()),
    )
    metric_row_1[1].metric(
        "Evaluaciones WOMAC totales",
        len(filtered_assessments),
    )
    metric_row_1[2].metric(
        "Mejoría media",
        (
            f"{average_improvement:.1f}%"
            if average_improvement is not None
            else "No calculable"
        ),
    )
    metric_row_1[3].metric(
        "Mediana",
        (
            f"{median_improvement:.1f}%"
            if median_improvement is not None
            else "No calculable"
        ),
    )
    metric_row_1[4].metric(
        "Desviación estándar",
        (
            f"{improvement_std:.1f}%"
            if improvement_std is not None
            else "No calculable"
        ),
    )

    metric_row_2 = st.columns(4)
    metric_row_2[0].metric(
        "Pacientes mejorados",
        improved_patients,
    )
    metric_row_2[1].metric(
        "Pacientes empeorados",
        int(response_counts.get("Empeorado", 0)),
    )
    metric_row_2[2].metric(
        "Pacientes sin cambios",
        int(response_counts.get("Sin cambios", 0)),
    )
    metric_row_2[3].metric(
        "No comparables",
        int(response_counts.get("No comparable", 0)),
    )

    st.markdown("#### Resultados por paciente")
    headers = st.columns([1.2, 1, 1, 1, 1.1, 1.2, 1.3])
    for column, label in zip(
        headers,
        [
            "Código",
            "WOMAC basal",
            "Último WOMAC",
            "Diferencia",
            "Mejoría",
            "Sesiones entre mediciones",
            "Respuesta clínica",
        ],
    ):
        column.markdown(f"**{label}**")

    badge_styles = {
        "Respondedor": ("#dcfce7", "#166534"),
        "Mejoría parcial": ("#ecfccb", "#3f6212"),
        "Sin cambios": ("#f3f4f6", "#374151"),
        "Empeorado": ("#fee2e2", "#991b1b"),
        "No comparable": ("#dbeafe", "#1e40af"),
    }
    for _, patient in summary.sort_values("patient_code").iterrows():
        row = st.columns([1.2, 1, 1, 1, 1.1, 1.2, 1.3])
        row[0].write(str(patient["patient_code"]))
        row[1].write(
            (
                f"{int(patient['baseline_womac'])}/96"
                if pd.notna(patient["baseline_womac"])
                else "Sin basal"
            )
        )
        row[2].write(f"{int(patient['latest_womac'])}/96")
        row[3].write(
            (
                f"{patient['absolute_difference']:+.1f}"
                if pd.notna(patient["absolute_difference"])
                else "No calculable"
            )
        )
        row[4].write(
            (
                f"{patient['improvement_percentage']:.1f}%"
                if pd.notna(patient["improvement_percentage"])
                else "No calculable"
            )
        )
        row[5].write(
            (
                int(patient["sessions_between"])
                if pd.notna(patient["sessions_between"])
                else "No calculable"
            )
        )
        response = str(patient["clinical_response"])
        background, foreground = badge_styles[response]
        row[6].markdown(
            (
                f'<span style="background:{background};color:{foreground};'
                'padding:0.2rem 0.55rem;border-radius:0.75rem;'
                f'font-weight:600;">{response}</span>'
            ),
            unsafe_allow_html=True,
        )

    st.markdown("#### Evolución promedio de la cohorte")
    group_evolution = (
        filtered_assessments.groupby("session_number", as_index=False)
        .agg(
            womac_average=("total_score", "mean"),
            patient_count=("patient_id", "nunique"),
        )
        .rename(
            columns={
                "session_number": "Sesión",
                "womac_average": "WOMAC promedio",
                "patient_count": "Pacientes",
            }
        )
    )
    group_figure = px.line(
        group_evolution,
        x="Sesión",
        y="WOMAC promedio",
        markers=True,
        hover_data=["Pacientes"],
        title="Evolución promedio WOMAC por sesión",
    )
    group_figure.update_xaxes(dtick=1)
    group_figure.update_yaxes(range=[0, 96], dtick=8)
    st.plotly_chart(group_figure, use_container_width=True)
    st.caption(
        "Cada punto muestra el promedio de las evaluaciones disponibles en "
        "esa sesión. La cantidad de pacientes puede variar entre sesiones."
    )

    st.markdown("#### Evolución WOMAC por sesiones")
    patient_codes = summary["patient_code"].sort_values().tolist()
    selected_code = st.selectbox(
        "Código del paciente",
        patient_codes,
        key="womac_dashboard_patient",
    )
    chart_data = filtered_assessments[
        filtered_assessments["patient_code"] == selected_code
    ][["session_number", "total_score", "assessment_type"]].rename(
        columns={
            "session_number": "Sesión",
            "total_score": "WOMAC total /96",
            "assessment_type": "Tipo",
        }
    )
    figure = px.line(
        chart_data,
        x="Sesión",
        y="WOMAC total /96",
        markers=True,
        hover_data=["Tipo"],
        title=f"Evolución WOMAC · {selected_code}",
    )
    figure.update_xaxes(dtick=1)
    figure.update_yaxes(range=[0, 96], dtick=8)
    st.plotly_chart(figure, use_container_width=True)


def render_dashboard() -> None:
    st.header("Resultados")
    show_medical_warning()
    st.warning(PSEUDONYMIZATION_WARNING)
    data = enrich_dashboard_data(get_dashboard_data())

    if data.empty:
        st.info("No hay pacientes registrados.")
        return

    selected_care_origin = st.selectbox(
        "Origen asistencial",
        ["Todos", "Hospital Avellaneda", "Consultorio Privado"],
        key="dashboard_care_origin",
    )
    if selected_care_origin != "Todos":
        data = data[data["care_origin"] == selected_care_origin].copy()
        if data.empty:
            st.info(
                "No hay pacientes registrados para el origen asistencial "
                "seleccionado."
            )
            return

    total_sessions = int(data["session_count"].sum())
    active_followups = int((data["session_count"] > 0).sum())
    col1, col2, col3 = st.columns(3)
    col1.metric("Pacientes registrados", len(data))
    col2.metric("Pacientes con seguimiento", active_followups)
    col3.metric("Sesiones registradas", total_sessions)

    eva_improved = int(
        (
            data["baseline_eva"].notna()
            & data["latest_eva"].notna()
            & (data["latest_eva"] < data["baseline_eva"])
        ).sum()
    )
    pgic_improved = int((data["latest_pgic"].fillna(0) >= 4).sum())
    analgesic_reduction = int(
        data["latest_analgesic_change"].isin(["Menos", "Mucho menos"]).sum()
    )
    patients_with_adverse_events = int(
        data["has_adverse_event"].fillna(0).astype(bool).sum()
    )
    agg1, agg2, agg3, agg4 = st.columns(4)
    agg1.metric("Pacientes con mejoría EVA", eva_improved)
    agg2.metric("Pacientes con mejoría PGIC", pgic_improved)
    agg3.metric("Reducción de analgésicos", analgesic_reduction)
    agg4.metric("Pacientes con eventos adversos", patients_with_adverse_events)

    render_womac_dashboard(selected_care_origin)

    data["latest_pgic_display"] = data["latest_pgic"].apply(format_pgic)
    data["latest_functional_impact_display"] = data[
        "latest_functional_impact"
    ].apply(format_functional_impact)
    data["clinical_category_display"] = data["clinical_category"].fillna(
        "Pendiente de clasificación"
    )
    data["clinical_subcategory_display"] = data["clinical_subcategory"].fillna(
        "Pendiente de clasificación"
    )
    data["suggested_prom_display"] = data["suggested_prom"].fillna(
        "Pendiente de clasificación"
    )
    data["care_origin_display"] = data["care_origin"].fillna(
        "Pendiente de clasificación"
    )
    display = data[
        [
            "patient_code",
            "care_origin_display",
            "clinical_category_display",
            "clinical_subcategory_display",
            "suggested_prom_display",
            "diagnosis",
            "baseline_eva",
            "latest_eva",
            "latest_pgic_display",
            "latest_functional_impact_display",
            "latest_analgesic_change",
            "latest_adverse_event_severity",
            "baseline_womac",
            "latest_womac",
            "womac_improvement_percentage",
            "improvement_percentage",
            "session_count",
            "clinical_status",
        ]
    ].rename(
        columns={
            "name": "Paciente",
            "dni": "DNI",
            "phone": "Teléfono",
            "patient_code": "Código de paciente",
            "care_origin_display": "Origen asistencial",
            "clinical_category_display": "Categoría",
            "clinical_subcategory_display": "Subcategoría",
            "suggested_prom_display": "PROM sugerido",
            "diagnosis": "Diagnóstico",
            "baseline_eva": "EVA basal",
            "latest_eva": "Última EVA",
            "latest_pgic_display": "Último PGIC",
            "latest_functional_impact_display": "Último impacto funcional",
            "latest_analgesic_change": "Cambio de analgésicos",
            "latest_adverse_event_severity": "Último evento adverso",
            "baseline_womac": "WOMAC basal",
            "latest_womac": "Último WOMAC",
            "womac_improvement_percentage": "Mejoría WOMAC (%)",
            "improvement_percentage": "Mejoría (%)",
            "session_count": "Sesiones",
            "clinical_status": "Estado clínico",
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "EVA basal": st.column_config.NumberColumn(format="%.1f"),
            "Última EVA": st.column_config.NumberColumn(format="%.1f"),
            "Mejoría (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "WOMAC basal": st.column_config.NumberColumn(format="%d/96"),
            "Último WOMAC": st.column_config.NumberColumn(format="%d/96"),
            "Mejoría WOMAC (%)": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

    st.subheader("Exportación para investigación")
    st.warning(PSEUDONYMIZATION_WARNING)
    research_data = get_pseudonymized_research_data()
    if not research_data.empty:
        research_data["adverse_event"] = research_data["adverse_event"].map(
            {0: "No", 1: "Sí"}
        ).fillna("Sin registro")
    st.download_button(
        "Descargar CSV seudonimizado",
        data=research_data.to_csv(index=False).encode("utf-8-sig"),
        file_name="prom_acu_investigacion_seudonimizada.csv",
        mime="text/csv",
    )

    st.subheader("Evolución individual")
    options = professional_patient_options(data)
    selected_label = st.selectbox(
        "Paciente para visualizar",
        list(options.keys()),
        key="dashboard_patient",
    )
    selected_id = options[selected_label]
    patient_row = data.loc[data["id"] == selected_id].iloc[0]
    sessions = get_patient_sessions(selected_id)
    womac_assessments = get_patient_womac_assessments(selected_id)

    st.info(
        f"**Categoría:** {patient_row['clinical_category_display']}  \n"
        f"**Subcategoría:** {patient_row['clinical_subcategory_display']}  \n"
        f"**PROM sugerido:** {patient_row['suggested_prom_display']}  \n"
        f"**Estado:** "
        f"{get_prom_implementation_status(patient_row['suggested_prom_display'])}"
    )

    st.subheader("Evolución WOMAC")
    if womac_assessments.empty:
        st.info("Este paciente todavía no tiene evaluaciones WOMAC.")
    else:
        womac_chart = womac_assessments[
            ["session_number", "total_score", "assessment_type"]
        ].rename(
            columns={
                "session_number": "Sesión",
                "total_score": "WOMAC total",
                "assessment_type": "Tipo",
            }
        )
        womac_figure = px.line(
            womac_chart,
            x="Sesión",
            y="WOMAC total",
            markers=True,
            hover_data=["Tipo"],
            title="Evolución WOMAC total",
        )
        womac_figure.update_yaxes(range=[0, 96], dtick=8)
        womac_figure.update_xaxes(dtick=1)
        st.plotly_chart(womac_figure, use_container_width=True)

    if sessions.empty:
        st.info("Este paciente todavía no tiene sesiones registradas.")
        return

    metric1, metric2, metric3, metric4, metric5, metric6 = st.columns(6)
    metric1.metric("EVA basal", f"{patient_row['baseline_eva']:.1f}")
    metric2.metric("Última EVA", f"{patient_row['latest_eva']:.1f}")
    metric3.metric(
        "Mejoría",
        f"{patient_row['improvement_percentage']:.1f}%",
    )
    metric4.metric("Estado", patient_row["clinical_status"])
    metric5.metric("Último PGIC", format_pgic(patient_row["latest_pgic"]))
    metric6.metric(
        "Impacto funcional",
        format_functional_impact(patient_row["latest_functional_impact"]),
    )

    chart_data = sessions[["session_number", "eva_pre"]].rename(
        columns={"session_number": "Sesión", "eva_pre": "EVA pre sesión"}
    )
    figure = px.line(
        chart_data,
        x="Sesión",
        y="EVA pre sesión",
        markers=True,
        title="Evolución del dolor",
    )
    figure.update_yaxes(range=[0, 10], dtick=1)
    figure.update_xaxes(dtick=1)
    figure.update_layout(hovermode="x unified")
    st.plotly_chart(figure, use_container_width=True)

    functional_data = sessions[
        ["session_number", "functional_impact"]
    ].dropna(subset=["functional_impact"])
    if not functional_data.empty:
        functional_chart = functional_data.rename(
            columns={
                "session_number": "Sesión",
                "functional_impact": "Impacto funcional global",
            }
        )
        functional_figure = px.line(
            functional_chart,
            x="Sesión",
            y="Impacto funcional global",
            markers=True,
            title="Evolución del impacto funcional global",
        )
        functional_figure.update_yaxes(range=[0, 10], dtick=1)
        functional_figure.update_xaxes(dtick=1)
        st.plotly_chart(functional_figure, use_container_width=True)
    else:
        st.info("No hay registros de impacto funcional global para este paciente.")

    st.subheader("Seguimiento clínico por sesión")
    clinical_history = sessions[
        [
            "session_number",
            "date",
            "pgic",
            "functional_impact",
            "medication_name",
            "medication_frequency",
            "analgesic_change",
            "adverse_event_severity",
            "adverse_event_description",
        ]
    ].copy()
    clinical_history["pgic"] = clinical_history["pgic"].apply(format_pgic)
    clinical_history["functional_impact"] = clinical_history[
        "functional_impact"
    ].apply(format_functional_impact)
    for column in (
        "medication_name",
        "medication_frequency",
        "analgesic_change",
        "adverse_event_severity",
        "adverse_event_description",
    ):
        clinical_history[column] = clinical_history[column].apply(
            format_optional_text
        )
    clinical_history = clinical_history.rename(
        columns={
            "session_number": "Sesión",
            "date": "Fecha",
            "pgic": "PGIC",
            "functional_impact": "Impacto funcional global",
            "medication_name": "Medicación relevante",
            "medication_frequency": "Frecuencia",
            "analgesic_change": "Cambio de analgésicos",
            "adverse_event_severity": "Evento adverso",
            "adverse_event_description": "Descripción",
        }
    )
    st.dataframe(clinical_history, use_container_width=True, hide_index=True)

    st.caption(
        f"Clasificación actual: "
        f"{clinical_status(patient_row['baseline_eva'], patient_row['latest_eva'])}."
    )

def render_report() -> None:
    st.header("Informe")
    show_medical_warning()
    patients = get_patients()

    if patients.empty:
        st.info("No hay pacientes registrados.")
        return

    report_type = st.radio(
        "Tipo de informe",
        [
            "Informe clínico identificado",
            "Informe seudonimizado para investigación",
        ],
    )
    pseudonymized = report_type == "Informe seudonimizado para investigación"
    if pseudonymized:
        st.warning(PSEUDONYMIZATION_WARNING)

    options = patient_options(patients)
    selected_label = st.selectbox(
        "Seleccionar paciente",
        list(options.keys()),
        key="report_patient",
    )
    patient_id = options[selected_label]
    patient = get_patient(patient_id)
    sessions = get_patient_sessions(patient_id)
    womac_assessments = get_patient_womac_assessments(patient_id)

    if patient is None:
        st.error("No se pudo recuperar la información del paciente.")
        return

    report = build_clinical_report(
        patient,
        sessions,
        womac_assessments=womac_assessments,
        pseudonymized=pseudonymized,
    )
    st.text_area("Vista previa", value=report, height=220, disabled=True)
    file_identity = patient["patient_code"]
    safe_name = "".join(
        character if character.isalnum() else "_"
        for character in file_identity.strip().lower()
    ).strip("_")
    st.download_button(
        "Descargar informe TXT",
        data=report.encode("utf-8"),
        file_name=f"informe_prom_acu_{safe_name or patient_id}.txt",
        mime="text/plain",
        type="primary",
    )
    st.caption(
        "Informe descriptivo de seguimiento. No constituye diagnóstico, "
        "indicación terapéutica ni certificado médico."
    )


def main() -> None:
    """Initialize storage and render the selected application page."""
    try:
        init_db()
        ensure_therapeutic_cycles_schema()
    except sqlite3.Error as error:
        st.error(f"No se pudo inicializar la base de datos: {error}")
        st.stop()

    guided_step = st.session_state.get("guided_step", "welcome")
    if guided_step == "welcome":
        render_welcome_step()
        return

    if guided_step == "professional_panel":
        render_professional_panel()
        return

    if guided_step == "returning_patient_search":
        render_returning_patient_search_step()
        return

    if guided_step == "followup_search":
        render_followup_search_step()
        return

    if guided_step == "followup_form":
        render_followup_form_step()
        return

    if guided_step == "followup_complete":
        render_followup_complete_step()
        return

    if guided_step == "consent":
        render_informed_consent_step()
        return

    if guided_step == "initial":
        render_initial_classification()
        return

    if guided_step == "personal_data":
        render_personal_data_step()
        return

    if guided_step == "problem_details":
        render_problem_details_step()
        return

    if guided_step == "follow_up_orientation":
        render_follow_up_orientation_step()
        return

    if guided_step == "adaptive_details":
        render_adaptive_details_step()
        return

    if guided_step == "global_functional_score":
        render_global_functional_score_step()
        return

    if guided_step == "treatment_expectations":
        render_treatment_expectations_step()
        return

    if guided_step == "thanks":
        render_thanks_step()
        return
    if guided_step == "final_closure":
        render_final_closure_step()
        return

    with st.sidebar:
        st.title("PROM-ACU")
        page = st.radio(
            "Navegación",
            [
                "Inicio",
                "Panel profesional",
                "Nuevo paciente",
                "Seguimiento del paciente",
                "Evaluación de dolor y movilidad",
                "Resultados",
                "Informe",
            ],
        )
        st.divider()
        st.caption("Demo MVP · Datos almacenados localmente")

    pages = {
        "Inicio": render_home,
        "Panel profesional": render_professional_panel,
        "Nuevo paciente": render_patient_registration,
        "Seguimiento del paciente": render_session_registration,
        "Evaluación de dolor y movilidad": render_womac_assessment,
        "Resultados": render_dashboard,
        "Informe": render_report,
    }
    pages[page]()


if __name__ == "__main__":
    main()
