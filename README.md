# PROM-ACU

Demo funcional en Streamlit para seguimiento clínico de pacientes tratados con
acupuntura mediante EVA, registro de sesiones, gráficos de evolución e informes
automáticos.

> **Advertencia médica:** Esta aplicación no reemplaza la consulta médica ni
> emite diagnósticos. Solo permite seguimiento clínico.

## Funcionalidades actuales

- Registro de pacientes.
- Clasificación clínica por categoría y subcategoría.
- Sugerencia automática del PROM correspondiente.
- Estado visible de los PROMs específicos: pendiente de implementación.
- Módulo WOMAC Fase 1 para carga resumida Likert 0-4.
- Código seudonimizado único para cada paciente (`PAC-000001`, etc.).
- Registro de EVA antes y después de cada sesión.
- Registro de PGIC (Patient Global Impression of Change) en cada sesión.
- Registro de impacto funcional global de 0 a 10.
- Registro de medicación relevante actual y frecuencia de uso.
- Comparación del consumo de analgésicos respecto del inicio.
- Registro de eventos adversos por severidad: ninguno, leve, moderado o severo.
- Observaciones clínicas.
- Cálculo de mejoría absoluta y porcentual.
- Clasificación descriptiva de la respuesta clínica.
- Dashboard con resumen por paciente.
- Indicadores agregados de mejoría EVA, mejoría PGIC, reducción de analgésicos
  y pacientes con eventos adversos.
- Modo de investigación que oculta nombre, DNI y teléfono.
- Gráficos de EVA e impacto funcional, más historial de PGIC.
- Gráfico de evolución WOMAC total.
- Informes identificados o seudonimizados descargables en TXT.
- Exportación CSV seudonimizada para investigación.
- Persistencia local en SQLite.

EVA, PGIC e impacto funcional global están implementados. WOMAC está
implementado en una primera fase de carga resumida. Los instrumentos KOOS, ODI,
NDI, SPADI, HAQ, FIQR, BASDAI, PSS-10, GAD-7, PHQ-9, ISI, IBS-SSS, ACT y CAT
solo se muestran como sugerencias clínicas y sus cuestionarios no se
administran.

## WOMAC Fase 1

La sección **Evaluación WOMAC** permite registrar, por `patient_code`:

- Tipo: Basal, Seguimiento o Final.
- Número de sesión.
- Dolor total de 0 a 20.
- Rigidez total de 0 a 8.
- Función física total de 0 a 68.

La aplicación calcula el total entre 0 y 96. Utiliza el marco Likert 0-4:

- 0: Ninguno.
- 1: Leve.
- 2: Moderado.
- 3: Severo.
- 4: Extremo.

Esta fase no administra todavía los 24 ítems individuales de WOMAC. El
Dashboard muestra WOMAC basal, último WOMAC, mejoría porcentual y un gráfico de
evolución. Si el basal es cero, la mejoría porcentual se informa como no
calculable.

PGIC se registra con la pregunta: “Comparado con el inicio del tratamiento,
¿cómo se encuentra hoy?”, usando una escala de 1 (Mucho peor) a 7
(Completamente mejor).

## Estructura

```text
PROM-ACU/
├── app.py
├── database.py
├── utils.py
├── requirements.txt
└── README.md
```

El archivo `prom_acu.db` se crea automáticamente al iniciar la aplicación.
Si la base ya existe, PROM-ACU ejecuta migraciones seguras para agregar:

- Categoría clínica, subcategoría y PROM sugerido a los pacientes.
- PGIC e impacto funcional global a las sesiones.
- Medicación, frecuencia, cambio de analgésicos y severidad de eventos adversos.
- Tabla independiente `womac_assessments` para evaluaciones WOMAC resumidas.

Los datos previos no se eliminan. Los valores históricos que no existían quedan
identificados como “Sin registro”. Los motivos anteriores con equivalencia
segura se migran a la nueva clasificación; los casos ambiguos permanecen
pendientes de clasificación profesional.

Los eventos adversos históricos registrados como “No” se migran a “Ninguno”.
Si una base anterior contiene un evento marcado como “Sí”, se conserva como
“No clasificado (histórico)” para no inventar una severidad retrospectiva.

La migración también genera automáticamente un `patient_code` único para cada
paciente existente sin eliminar nombre, DNI ni teléfono.

## Modo investigación y seudonimización

En el Dashboard médico, active **Modo investigación / anonimizado** para:

- Mostrar el código del paciente en lugar de su nombre.
- Ocultar DNI y teléfono.
- Trabajar con vistas de seguimiento seudonimizadas.

En **Informe clínico** puede elegir entre:

- Informe clínico identificado.
- Informe seudonimizado para investigación.

La exportación CSV de investigación incluye código, variables demográficas y
datos clínicos por sesión. No exporta nombre, DNI ni teléfono.

> Los datos seudonimizados reducen el riesgo de identificación, pero no
> equivalen necesariamente a anonimización irreversible.

El diagnóstico y otras variables clínicas también pueden facilitar una
reidentificación cuando se combinan con información externa. El acceso y uso de
las exportaciones debe estar controlado.

## Ejecución local

Se requiere Python 3.10 o superior.

1. Crear un entorno virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Instalar dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

3. Iniciar la aplicación:

   ```powershell
   streamlit run app.py
   ```

4. Abrir la dirección que Streamlit muestra, normalmente
   `http://localhost:8501`.

## Datos y privacidad

La demo guarda datos en `prom_acu.db` dentro del directorio del proyecto. No
incluye autenticación, cifrado, auditoría, copias de seguridad ni gestión de
consentimiento. Antes de usarla con datos reales deben incorporarse controles
de acceso, protección de datos personales y las medidas regulatorias aplicables.

No se recomienda versionar la base de datos. Puede agregarse esta línea a
`.gitignore`:

```text
prom_acu.db
```

## Despliegue en Streamlit Community Cloud

1. Subir el proyecto a un repositorio de GitHub.
2. Ingresar en [Streamlit Community Cloud](https://share.streamlit.io/).
3. Crear una aplicación y seleccionar el repositorio, la rama y `app.py`.
4. Confirmar que `requirements.txt` esté en la raíz y desplegar.

SQLite funciona para una demo, pero el almacenamiento local de Community Cloud
no debe considerarse persistente. Para un entorno real conviene usar una base
de datos externa administrada y añadir autenticación, autorización, cifrado,
backups y trazabilidad de cambios.

## Alcance clínico

PROM-ACU registra y presenta información aportada por el profesional. No
inventa diagnósticos, no recomienda tratamientos y no reemplaza el juicio
clínico ni la consulta médica.
