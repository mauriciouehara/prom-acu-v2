"""Clinical rules and presentation helpers for PROM-ACU."""

from __future__ import annotations

from typing import Any

import pandas as pd


CLINICAL_CLASSIFICATION = {
    "Musculoesquelético": {
        "Rodilla": "WOMAC / KOOS",
        "Cadera": "WOMAC",
        "Lumbar": "ODI",
        "Cervical": "NDI",
        "Hombro": "SPADI",
        "Dolor musculoesquelético generalizado": (
            "EVA + PGIC + impacto funcional global"
        ),
    },
    "Reumatología": {
        "Artrosis generalizada": "WOMAC + EVA + PGIC",
        "Artritis reumatoidea": "HAQ",
        "Espondiloartritis": "BASDAI",
        "Fibromialgia": "FIQR",
        "Otra enfermedad reumatológica": (
            "EVA + PGIC + impacto funcional global"
        ),
    },
    "Salud mental y sueño": {
        "Estrés": "PSS-10",
        "Ansiedad": "GAD-7",
        "Depresión": "PHQ-9",
        "Insomnio": "ISI",
    },
    "Digestivo funcional": {
        "Colon irritable": "IBS-SSS",
        "Dispepsia funcional": "PAGI-SYM",
        "Reflujo": "GERD-Q",
        "Estreñimiento funcional": "PAC-SYM",
    },
    "Respiratorio funcional": {
        "Asma": "ACT",
        "EPOC": "CAT",
        "Rinitis": "SNOT-22 o mini-RQLQ",
        "Disnea funcional": "mMRC",
    },
    "Otros / Integrativo": {
        "Fatiga crónica": "FSS",
        "Post-COVID": "EQ-5D + FSS",
        "Cefalea / migraña": "HIT-6",
        "Neuropatía": "EVA + impacto funcional global",
        "Otro": "EVA + PGIC + impacto funcional global",
    },
}

SCALE_BY_COMPLAINT = {
    "Rodilla": "KOOS / WOMAC + EVA",
    "Cadera": "WOMAC + EVA",
    "Lumbalgia": "ODI + EVA",
    "Cervicalgia": "NDI + EVA",
    "Hombro": "SPADI + EVA",
    "Dolor general": "EVA + PGIC",
    "Estrés / ansiedad": "GAD-7 + PSS",
    "Insomnio": "ISI",
    "Digestivo funcional": "IBS-SSS",
    "Respiratorio funcional": "ACT o CAT",
}

MEDICAL_WARNING = (
    "Esta aplicación no reemplaza la consulta médica ni emite diagnósticos. "
    "Solo permite seguimiento clínico."
)

PSEUDONYMIZATION_WARNING = (
    "Los datos seudonimizados reducen el riesgo de identificación, pero no "
    "equivalen necesariamente a anonimización irreversible."
)

PGIC_OPTIONS = {
    1: "Mucho peor",
    2: "Peor",
    3: "Igual",
    4: "Levemente mejor",
    5: "Moderadamente mejor",
    6: "Mucho mejor",
    7: "Completamente mejor",
}

ANALGESIC_CHANGE_OPTIONS = [
    "Mucho más",
    "Más",
    "Igual",
    "Menos",
    "Mucho menos",
    "No usa",
]

ADVERSE_EVENT_SEVERITY_OPTIONS = [
    "Ninguno",
    "Leve",
    "Moderado",
    "Severo",
]


def assigned_scale(main_complaint: str) -> str:
    """Return the scale configured for a main complaint."""
    return SCALE_BY_COMPLAINT.get(main_complaint, "Pendiente de asignación")


def get_suggested_prom(category: str, subcategory: str) -> str:
    """Return the informational PROM configured for a classification."""
    return CLINICAL_CLASSIFICATION.get(category, {}).get(
        subcategory,
        "Pendiente de clasificación",
    )


def get_prom_implementation_status(suggested_prom: str) -> str:
    """Return the current implementation status for a suggested PROM."""
    if "WOMAC" in str(suggested_prom or ""):
        return (
            "WOMAC Fase 1 disponible: carga resumida. "
            "Los 24 ítems todavía no están implementados."
        )
    return "Pendiente de implementación."


def calculate_improvement(
    baseline_eva: float | int | None,
    current_eva: float | int | None,
) -> tuple[float | None, float | None]:
    """Calculate absolute and percentage improvement from EVA values."""
    if baseline_eva is None or current_eva is None:
        return None, None

    baseline = float(baseline_eva)
    current = float(current_eva)
    absolute = baseline - current

    if baseline == 0:
        percentage = 0.0 if current == 0 else -100.0
    else:
        percentage = (absolute / baseline) * 100

    return round(absolute, 1), round(percentage, 1)


def calculate_womac_improvement(
    baseline_score: float | int | None,
    current_score: float | int | None,
) -> tuple[float | None, float | None]:
    """Calculate WOMAC improvement without changing EVA logic."""
    if (
        baseline_score is None
        or current_score is None
        or pd.isna(baseline_score)
        or pd.isna(current_score)
    ):
        return None, None

    baseline = float(baseline_score)
    current = float(current_score)
    absolute = baseline - current
    percentage = None if baseline == 0 else (absolute / baseline) * 100
    return round(absolute, 1), (
        round(percentage, 1) if percentage is not None else None
    )


def clinical_status(
    baseline_eva: float | int | None,
    current_eva: float | int | None,
) -> str:
    """Classify the clinical response according to MVP thresholds."""
    if baseline_eva is None or current_eva is None:
        return "Sin sesiones"

    baseline = float(baseline_eva)
    current = float(current_eva)
    if current > baseline:
        return "Empeoramiento"

    _, percentage = calculate_improvement(baseline, current)
    if percentage is None:
        return "Sin datos"
    if percentage >= 70:
        return "Excelente respuesta"
    if percentage >= 50:
        return "Muy buena respuesta"
    if percentage >= 30:
        return "Moderada"
    if percentage >= 10:
        return "Leve"
    return "Sin respuesta clara"


def enrich_dashboard_data(data: pd.DataFrame) -> pd.DataFrame:
    """Add calculated improvement and status columns to dashboard data."""
    result = data.copy()
    if result.empty:
        return result

    calculations = result.apply(
        lambda row: calculate_improvement(row["baseline_eva"], row["latest_eva"]),
        axis=1,
    )
    result["absolute_improvement"] = calculations.apply(lambda value: value[0])
    result["improvement_percentage"] = calculations.apply(lambda value: value[1])
    result["clinical_status"] = result.apply(
        lambda row: clinical_status(row["baseline_eva"], row["latest_eva"]),
        axis=1,
    )
    womac_calculations = result.apply(
        lambda row: calculate_womac_improvement(
            row["baseline_womac"],
            row["latest_womac"],
        ),
        axis=1,
    )
    result["womac_absolute_improvement"] = womac_calculations.apply(
        lambda value: value[0]
    )
    result["womac_improvement_percentage"] = womac_calculations.apply(
        lambda value: value[1]
    )
    return result


def yes_no(value: Any) -> str:
    """Convert SQLite booleans to Spanish text."""
    return "Sí" if bool(value) else "No"


def format_pgic(value: Any) -> str:
    """Return a readable PGIC value, including its numeric score."""
    if value is None or pd.isna(value):
        return "Sin registro"

    try:
        score = int(value)
    except (TypeError, ValueError):
        return "Sin registro"

    label = PGIC_OPTIONS.get(score)
    return f"{score}. {label}" if label else "Sin registro"


def format_functional_impact(value: Any) -> str:
    """Return a readable global functional impact value."""
    if value is None or pd.isna(value):
        return "Sin registro"

    try:
        return f"{float(value):.1f}/10"
    except (TypeError, ValueError):
        return "Sin registro"


def format_optional_text(value: Any) -> str:
    """Return a normalized display value for optional session text."""
    if value is None or pd.isna(value) or not str(value).strip():
        return "Sin registro"
    return str(value).strip()


def build_clinical_report(
    patient: dict[str, Any],
    sessions: pd.DataFrame,
    womac_assessments: pd.DataFrame | None = None,
    pseudonymized: bool = False,
) -> str:
    """Build a plain-text clinical follow-up report."""
    category = patient.get("clinical_category") or "Pendiente de clasificación"
    subcategory = (
        patient.get("clinical_subcategory") or "Pendiente de clasificación"
    )
    suggested_prom = patient.get("suggested_prom") or "Pendiente de clasificación"
    prom_status = get_prom_implementation_status(suggested_prom)
    identity = f"Paciente {patient.get('patient_code') or 'Sin código'}"

    womac_block = build_womac_report_block(womac_assessments)

    if sessions.empty:
        report = (
            f"{identity}, diagnóstico {patient['diagnosis']}, "
            f"categoría clínica {category}, subcategoría {subcategory}. "
            f"PROM sugerido: {suggested_prom}. Estado: {prom_status} "
            "Paciente registrado/a para seguimiento con acupuntura. "
            "Aún no cuenta con sesiones ni valores EVA registrados."
        )
        return f"{report}{womac_block}"

    baseline_eva = float(sessions.iloc[0]["eva_pre"])
    latest_session = sessions.iloc[-1]
    latest_eva = float(latest_session["eva_pre"])
    _, percentage = calculate_improvement(baseline_eva, latest_eva)
    status = clinical_status(baseline_eva, latest_eva)
    notes = str(latest_session["notes"]).strip() or "Sin observaciones registradas"
    pgic = format_pgic(latest_session.get("pgic"))
    functional_impact = format_functional_impact(
        latest_session.get("functional_impact")
    )
    medication_name = format_optional_text(latest_session.get("medication_name"))
    medication_frequency = format_optional_text(
        latest_session.get("medication_frequency")
    )
    analgesic_change = format_optional_text(
        latest_session.get("analgesic_change")
    )
    adverse_severity = format_optional_text(
        latest_session.get("adverse_event_severity")
    )
    adverse_description = (
        "Omitida en el informe seudonimizado para reducir el riesgo de "
        "identificación"
        if pseudonymized
        else format_optional_text(
            latest_session.get("adverse_event_description")
        )
    )
    observations = (
        "Omitidas en el informe seudonimizado para reducir el riesgo de "
        "identificación"
        if pseudonymized
        else notes
    )

    report = (
        f"{identity}, diagnóstico {patient['diagnosis']}, "
        f"categoría clínica {category}, subcategoría {subcategory}. "
        f"PROM sugerido: {suggested_prom}. Estado: {prom_status} "
        f"En seguimiento con acupuntura. EVA basal: {baseline_eva:.1f}. "
        f"Última EVA registrada: {latest_eva:.1f}. "
        f"Mejoría porcentual: {percentage:.1f}%. "
        f"Respuesta clínica: {status}. "
        f"PGIC más reciente: {pgic}. "
        f"Último impacto funcional global: {functional_impact}. "
        f"Medicación relevante actual: {medication_name}. "
        f"Frecuencia de uso: {medication_frequency}. "
        f"Consumo de analgésicos comparado con el inicio: {analgesic_change}. "
        f"Evento adverso más reciente: {adverse_severity}. "
        f"Descripción del evento adverso: {adverse_description}. "
        f"Observaciones: {observations}."
    )
    return f"{report}{womac_block}"


def build_womac_report_block(
    womac_assessments: pd.DataFrame | None,
) -> str:
    """Build an optional summarized WOMAC block for the clinical report."""
    if womac_assessments is None or womac_assessments.empty:
        return ""

    ordered = womac_assessments.sort_values(["session_number", "id"])
    basal_rows = ordered.loc[ordered["assessment_type"] == "Basal"]
    if basal_rows.empty:
        baseline = None
        baseline_label = "Sin evaluación basal"
    else:
        baseline = basal_rows.iloc[0]
        baseline_label = f"{int(baseline['total_score'])}/96"

    latest = ordered.iloc[-1]
    _, percentage = calculate_womac_improvement(
        baseline["total_score"] if baseline is not None else None,
        latest["total_score"],
    )
    improvement_label = (
        f"{percentage:.1f}%"
        if percentage is not None
        else "No calculable"
    )

    return (
        " WOMAC Likert 0-4: "
        f"basal {baseline_label}; "
        f"último {int(latest['total_score'])}/96 "
        f"({latest['assessment_type']}, sesión "
        f"{int(latest['session_number'])}); "
        f"dolor {int(latest['pain_score'])}/20; "
        f"rigidez {int(latest['stiffness_score'])}/8; "
        f"función {int(latest['function_score'])}/68; "
        f"mejoría WOMAC {improvement_label}."
    )
