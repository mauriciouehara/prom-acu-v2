"""PROM-ACU: simple clinical follow-up demo built with Streamlit."""

from __future__ import annotations

import importlib
import sqlite3
from datetime import date

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
    if st.button(
        "Comenzar",
        type="primary",
        use_container_width=True,
        disabled=not accepted_consent,
    ):
        st.session_state["informed_consent_accepted"] = True
        st.session_state["guided_step"] = "initial"
        st.rerun()


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
    if st.button(
        "Continuar",
        type="primary",
        use_container_width=True,
        disabled=(
            selected_category is None
            or (
                selected_category == "Otro problema de salud"
                and not other_health_problem_description.strip()
            )
        ),
    ):
        st.session_state["selected_initial_category"] = selected_category
        if selected_category == "Otro problema de salud":
            st.session_state["other_health_problem_description"] = (
                other_health_problem_description.strip()
            )
        st.session_state["guided_step"] = "personal_data"
        st.rerun()


def render_personal_data_step() -> None:
    """Collect simple personal data for the guided experience."""
    hide_sidebar()
    st.title("Datos personales")
    st.success("Perfecto. Vamos a completar una breve evaluación.")

    guided_name = st.text_input("Apellido y nombre completo *", max_chars=120)
    guided_dni = st.text_input("DNI *", max_chars=30)
    guided_phone = st.text_input(
        "Teléfono celular / WhatsApp o contacto de familiar *",
        max_chars=60,
    )
    guided_email = st.text_input("E-mail", max_chars=120)
    guided_age = st.text_input("Edad *", max_chars=3)
    guided_sex = st.selectbox(
        "Sexo *",
        [
            "Femenino",
            "Masculino",
            "Intersexual",
            "Otro",
            "Prefiere no informar",
        ],
        index=None,
        placeholder="Seleccione una opción",
    )
    missing_required_data = (
        not guided_name.strip()
        or not guided_dni.strip()
        or not guided_phone.strip()
        or not guided_age.strip().isdigit()
        or int(guided_age.strip()) > 120
        or not guided_sex
    )

    if st.button(
        "Siguiente",
        type="primary",
        use_container_width=True,
        disabled=missing_required_data,
    ):
        st.session_state["guided_personal_data"] = {
            "name": guided_name.strip(),
            "age": int(guided_age.strip()),
            "sex": guided_sex,
            "dni": guided_dni.strip(),
            "phone": guided_phone.strip(),
            "email": guided_email.strip(),
        }
        st.session_state["guided_step"] = "problem_details"
        st.rerun()


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
                index=None,
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
            index=None,
            placeholder="Seleccione una opción",
        )
        intensity = st.slider(
            slider_label,
            min_value=0,
            max_value=10,
            value=0,
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


def render_follow_up_orientation_step() -> None:
    """Collect simple context to orient the patient follow-up."""
    hide_sidebar()
    st.title("Para orientar mejor el seguimiento")

    with st.form("guided_follow_up_orientation_form"):
        worsens_with = st.text_input(
            "¿Qué empeora su problema?",
            placeholder="Ejemplo: caminar, estrés, comida, frío, noche, esfuerzo.",
        )
        improves_with = st.text_input(
            "¿Qué mejora su problema?",
            placeholder="Ejemplo: reposo, calor, medicación, masajes, dormir.",
        )
        medication_related = st.radio(
            "¿Toma actualmente algún medicamento relacionado con este problema?",
            ["No", "Sí", "No estoy seguro/a"],
            index=None,
        )
        medication_name = ""
        if medication_related == "Sí":
            medication_name = st.text_input("¿Cuál?")
        daily_limitation = st.radio(
            "¿Este problema limita sus actividades diarias?",
            ["No", "Un poco", "Bastante", "Mucho"],
            index=None,
        )
        submitted = st.form_submit_button(
            "Finalizar",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not medication_related or not daily_limitation:
            st.error("Complete las opciones para finalizar.")
            return
        if medication_related == "Sí" and not medication_name.strip():
            st.error("Indique cuál medicamento toma.")
            return

        medication_summary = medication_related
        if medication_related == "Sí":
            medication_summary = medication_name.strip()

        st.session_state["guided_follow_up_orientation"] = {
            "worsens_with": worsens_with.strip() or "Sin completar",
            "improves_with": improves_with.strip() or "Sin completar",
            "medication_related": medication_summary,
            "daily_limitation": daily_limitation,
        }
        if st.session_state.get("selected_initial_category") == "Otro problema de salud":
            st.session_state["guided_step"] = "treatment_expectations"
        else:
            st.session_state["guided_step"] = "adaptive_details"
        st.rerun()


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
                ["Trabajo", "Familia", "Economía", "Salud", "No lo sé"],
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
        st.session_state["guided_step"] = "treatment_expectations"
        st.rerun()

    answers = {}
    with st.form("guided_adaptive_details_form"):
        for key, question, options in questions:
            answers[key] = {
                "question": question,
                "answer": st.radio(question, options, index=None),
            }
        submitted = st.form_submit_button(
            "Continuar",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if any(not item["answer"] for item in answers.values()):
            st.error("Complete las opciones para continuar.")
            return
        st.session_state["guided_adaptive_details"] = answers
        st.session_state["guided_step"] = "treatment_expectations"
        st.rerun()


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

    selected_expectations = st.multiselect(
        "Seleccione todas las opciones que correspondan",
        expectation_options,
    )
    other_expectation = ""
    if "Otro objetivo" in selected_expectations:
        other_expectation = st.text_area(
            "Describa brevemente cuál sería el resultado ideal para usted",
            max_chars=500,
        )
    daily_life_result = st.text_area(
        "Si el tratamiento fuera exitoso, dentro de 3 a 6 meses, ¿qué sería "
        "diferente en su vida cotidiana?",
        max_chars=800,
    )
    missing_expectations = (
        not selected_expectations
        or (
            "Otro objetivo" in selected_expectations
            and not other_expectation.strip()
        )
        or not daily_life_result.strip()
    )

    if st.button(
        "Continuar",
        type="primary",
        use_container_width=True,
        disabled=missing_expectations,
    ):
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
        st.session_state["guided_step"] = "thanks"
        st.rerun()


def clear_guided_flow() -> None:
    """Clear temporary guided intake data from the Streamlit session."""
    for key in (
        "informed_consent_accepted",
        "informed_consent_checkbox",
        "selected_initial_category",
        "initial_category_selection",
        "other_health_problem_description_input",
        "other_health_problem_description",
        "guided_personal_data",
        "guided_problem_details",
        "guided_follow_up_orientation",
        "guided_adaptive_details",
        "guided_treatment_expectations",
        "guided_step",
    ):
        st.session_state.pop(key, None)


def render_thanks_step() -> None:
    """Render the patient-friendly completion screen."""
    hide_sidebar()
    st.title("Gracias")
    st.success("Su información fue registrada correctamente.")
    st.write(
        "El Dr. Mauricio Uehara podrá revisar estos datos para orientar mejor "
        "el seguimiento."
    )

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
    st.markdown("### Resumen")
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
    st.write(f"**Expectativas del tratamiento:** {expectations_text}")
    st.write(
        f"**Resultado esperado en la vida cotidiana:** "
        f"{treatment_expectations.get('daily_life_result', 'Sin completar')}"
    )

    if st.button(
        "Enviar otra respuesta",
        type="primary",
        use_container_width=True,
    ):
        clear_guided_flow()
        st.rerun()


def patient_options(patients: pd.DataFrame) -> dict[str, int]:
    """Build pseudonymized patient labels mapped to database identifiers."""
    return {
        str(row["patient_code"]): int(row["id"])
        for _, row in patients.iterrows()
    }


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
            add_session(
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
    options = {
        str(row["patient_code"]): int(row["id"])
        for _, row in data.iterrows()
    }
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
    except sqlite3.Error as error:
        st.error(f"No se pudo inicializar la base de datos: {error}")
        st.stop()

    guided_step = st.session_state.get("guided_step", "consent")
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

    if guided_step == "treatment_expectations":
        render_treatment_expectations_step()
        return

    if guided_step == "thanks":
        render_thanks_step()
        return

    with st.sidebar:
        st.title("PROM-ACU")
        page = st.radio(
            "Navegación",
            [
                "Inicio",
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
        "Nuevo paciente": render_patient_registration,
        "Seguimiento del paciente": render_session_registration,
        "Evaluación de dolor y movilidad": render_womac_assessment,
        "Resultados": render_dashboard,
        "Informe": render_report,
    }
    pages[page]()


if __name__ == "__main__":
    main()
