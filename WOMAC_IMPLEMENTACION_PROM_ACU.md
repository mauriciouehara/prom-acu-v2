# DISEÑO DE IMPLEMENTACIÓN DE WOMAC EN PROM-ACU

## 1. Propósito

Este documento diseña la incorporación de WOMAC como primer PROM específico
validado en PROM-ACU para pacientes con compromiso de rodilla o cadera,
especialmente aquellos con gonartrosis o artrosis documentada.

La implementación debe integrarse con el seguimiento clínico existente sin
reemplazar:

- EVA.
- PGIC.
- Impacto funcional global.
- Medicación y consumo de analgésicos.
- Eventos adversos.
- Clasificación clínica.
- Seudonimización mediante `patient_code`.

> PROM-ACU no utilizará WOMAC para emitir diagnósticos. El instrumento medirá
> síntomas y limitación funcional reportados por el paciente.

---

## 2. Condición previa: versión, licencia y autorización

WOMAC es un instrumento estandarizado. Antes de implementarlo deben confirmarse:

- Titular y condiciones de licencia.
- Autorización para uso clínico, académico o comercial.
- Versión exacta que utilizará PROM-ACU.
- Idioma y traducción validada.
- Formato de respuesta autorizado.
- Instrucciones oficiales.
- Período de recuerdo.
- Algoritmo oficial de puntuación.
- Reglas para respuestas incompletas.
- Permiso para administración electrónica.

Este documento no reproduce el texto literal de los ítems. Las preguntas
exactas solo deberán incorporarse desde una fuente oficial y autorizada.

### Decisión necesaria antes de programar

Debe elegirse una única versión operativa, por ejemplo:

- Likert de cinco niveles.
- Escala visual analógica.
- Otra versión oficialmente autorizada.

No se deben mezclar versiones ni convertir puntuaciones entre formatos sin una
regla validada y documentada.

---

## 3. Población elegible

WOMAC podrá sugerirse para:

- Musculoesquelético > Rodilla.
- Musculoesquelético > Cadera.
- Reumatología > Artrosis generalizada.
- Gonartrosis documentada.
- Coxartrosis documentada.

### Reglas de elegibilidad

1. La clasificación clínica debe estar confirmada.
2. El diagnóstico específico se conserva como dato independiente.
3. La app puede sugerir WOMAC, pero el profesional debe activarlo.
4. WOMAC no debe administrarse automáticamente a toda persona con dolor de
   rodilla o cadera sin confirmar que el instrumento sea apropiado.
5. Si se elige KOOS para un protocolo de rodilla, debe evitarse la duplicación
   innecesaria con WOMAC.

---

## 4. Dónde se cargará WOMAC

Se propone crear una nueva sección principal:

> **Evaluaciones PROM**

Esta sección estará separada de Registro de sesión para no sobrecargar la
consulta cotidiana.

## 4.1 Pantalla “Evaluaciones PROM”

La pantalla mostrará:

- Selector de paciente por `patient_code`.
- Categoría y subcategoría.
- Diagnóstico registrado.
- PROMs sugeridos.
- PROMs activados.
- Próxima evaluación pendiente.
- Historial de evaluaciones.
- Botón “Iniciar WOMAC”.

## 4.2 Flujo de carga

1. Seleccionar paciente mediante `patient_code`.
2. Confirmar que WOMAC está activado.
3. Elegir el momento de aplicación:
   - Basal.
   - Seguimiento.
   - Final.
4. Mostrar instrucciones oficiales.
5. Cargar las respuestas por subescala.
6. Revisar respuestas faltantes.
7. Confirmar el envío.
8. Calcular y guardar resultados.
9. Mostrar un resumen sin interpretación diagnóstica.

## 4.3 Acceso desde el paciente

En una versión futura con portal del paciente, WOMAC podrá administrarse
remotamente. En la primera implementación será cargado por el profesional o en
un dispositivo supervisado.

---

## 5. Cuándo se aplicará

La periodicidad debe ser configurable por protocolo. Se propone la siguiente
regla inicial.

## 5.1 Evaluación basal

Aplicar WOMAC:

- Antes de la primera sesión.
- En la primera sesión, antes de la intervención.
- O dentro de una ventana basal máxima definida por protocolo.

La evaluación basal debe quedar marcada de forma explícita. No debe inferirse
únicamente por ser el registro más antiguo.

## 5.2 Seguimiento periódico

Propuesta inicial:

> Repetir cada 4 sesiones.

Ejemplos:

- Sesión 4.
- Sesión 8.
- Sesión 12.

La frecuencia debe poder configurarse:

- Cada 4 sesiones.
- Cada 6 sesiones.
- Cada período temporal.
- Según protocolo de investigación.

Si una evaluación no se completa en la sesión prevista, debe permanecer
pendiente y registrar la demora.

## 5.3 Control final

Aplicar WOMAC:

- Al alta.
- Al cierre del ciclo de tratamiento.
- Ante interrupción documentada.
- En una evaluación final definida por el protocolo.

El control final puede coincidir con una evaluación periódica, pero no debe
duplicarse. Se guardará como tipo `final`.

## 5.4 Seguimiento posterior

Una versión futura podrá incorporar controles posteriores, por ejemplo:

- 30 días.
- 90 días.
- 6 meses.

Estos momentos no forman parte de la primera implementación.

---

## 6. Estructura clínica de WOMAC

WOMAC comprende 24 ítems distribuidos en tres subescalas:

| Subescala | Cantidad de ítems |
|---|---:|
| Dolor | 5 |
| Rigidez | 2 |
| Función física | 17 |
| **Total** | **24** |

## 6.1 Dolor

Evalúa dolor durante actividades o situaciones definidas por la versión oficial
del instrumento.

La app deberá:

- Mostrar los 5 ítems oficiales.
- Conservar su orden.
- Mantener la redacción validada.
- Usar el mismo período de recuerdo.

## 6.2 Rigidez

Evalúa rigidez mediante 2 ítems oficiales.

La app no debe modificar las expresiones ni agregar interpretaciones propias.

## 6.3 Función física

Evalúa dificultad para realizar actividades mediante 17 ítems oficiales.

La interfaz puede dividir esta sección en páginas para mejorar la usabilidad,
pero deberá preservar:

- Numeración.
- Orden.
- Opciones de respuesta.
- Instrucciones.

---

## 7. Diseño UX del cuestionario

## 7.1 Presentación

Se recomienda:

- Una subescala por bloque.
- Barra de progreso.
- Número de ítem actual.
- Opciones de respuesta claramente separadas.
- Botones grandes para uso táctil.
- Posibilidad de guardar como borrador.
- Revisión final antes del envío.

## 7.2 Respuestas obligatorias

La primera versión debe solicitar respuesta para todos los ítems.

Si el protocolo oficial permite puntuación con datos faltantes, esa regla
deberá implementarse explícitamente. No se deben imputar respuestas.

## 7.3 Estados de evaluación

- Pendiente.
- En progreso.
- Completa.
- Incompleta.
- Anulada.
- Cerrada.

Solo una evaluación completa y válida debe utilizarse para calcular mejoría.

## 7.4 Información visible

Antes de comenzar:

> WOMAC es un cuestionario de seguimiento de dolor, rigidez y función física.
> No emite diagnósticos ni reemplaza la evaluación profesional.

---

## 8. Sistema de puntaje

El algoritmo dependerá de la versión autorizada.

## 8.1 Diseño recomendado: versión Likert 0–4

Si se autoriza la versión Likert de cinco niveles, cada respuesta se codificará:

| Respuesta | Puntaje |
|---|---:|
| Ninguno | 0 |
| Leve | 1 |
| Moderado | 2 |
| Severo | 3 |
| Extremo | 4 |

La terminología exacta debe coincidir con la traducción oficial.

## 8.2 Rangos brutos

Para la versión Likert 0–4:

| Subescala | Ítems | Rango bruto |
|---|---:|---:|
| Dolor | 5 | 0–20 |
| Rigidez | 2 | 0–8 |
| Función física | 17 | 0–68 |
| Total | 24 | 0–96 |

Un puntaje mayor representa mayor dolor, rigidez o limitación funcional.

## 8.3 Puntaje normalizado

Además del puntaje bruto, PROM-ACU puede almacenar una transformación 0–100:

**Puntaje normalizado = (puntaje bruto / máximo posible) × 100**

Interpretación:

- 0 = ausencia de afectación medida.
- 100 = máxima afectación posible en esa escala.

La app deberá indicar siempre si muestra:

- Puntaje bruto.
- Puntaje normalizado.

No se deben presentar ambos sin etiquetas claras.

## 8.4 Versión VAS

Si se utiliza una versión VAS, los rangos y cálculos serán diferentes. El motor
de puntuación deberá identificar la versión y aplicar únicamente su algoritmo.

---

## 9. Cálculos

## 9.1 Subescala dolor

Para Likert 0–4:

**Dolor bruto = suma de los 5 ítems de dolor**

**Dolor 0–100 = (dolor bruto / 20) × 100**

## 9.2 Subescala rigidez

**Rigidez bruta = suma de los 2 ítems de rigidez**

**Rigidez 0–100 = (rigidez bruta / 8) × 100**

## 9.3 Subescala función física

**Función bruta = suma de los 17 ítems de función**

**Función 0–100 = (función bruta / 68) × 100**

## 9.4 Puntaje total

**Total bruto = dolor + rigidez + función**

Para Likert 0–4:

**Total bruto máximo = 96**

**Total 0–100 = (total bruto / 96) × 100**

El total debe calcularse únicamente si la versión y sus reglas oficiales lo
permiten.

## 9.5 Mejoría absoluta

Como un puntaje menor representa menor afectación:

**Mejoría absoluta = puntaje basal − puntaje actual**

Un valor positivo indica mejoría.

## 9.6 Mejoría porcentual

**Mejoría porcentual = ((puntaje basal − puntaje actual) / puntaje basal) × 100**

Reglas:

- Calcular por separado para total y subescalas.
- Si el basal es cero, no aplicar la fórmula porcentual convencional.
- Si basal y actual son cero, informar “sin cambio, puntaje 0”.
- Si el puntaje actual es mayor, informar empeoramiento.
- No reemplazar valores faltantes por cero.

## 9.7 Resultados que se almacenarán

Para cada evaluación:

- Dolor bruto.
- Dolor normalizado.
- Rigidez bruta.
- Rigidez normalizada.
- Función bruta.
- Función normalizada.
- Total bruto.
- Total normalizado.
- Mejoría absoluta desde basal.
- Mejoría porcentual desde basal.

Los cálculos de mejoría pueden generarse al consultar los datos, pero se
recomienda guardar la versión del algoritmo para garantizar reproducibilidad.

---

## 10. Identificación de la evaluación basal

La comparación debe utilizar:

1. La evaluación WOMAC marcada como basal.
2. Completa.
3. Válida.
4. Correspondiente a la misma versión.

No se deben comparar:

- Versiones diferentes.
- Escalas Likert y VAS.
- Evaluaciones anuladas.
- Evaluaciones incompletas sin regla autorizada.

Si existe más de una evaluación basal, la app debe generar una alerta de
integridad.

---

## 11. Dashboard

## 11.1 Tabla general

Agregar columnas opcionales:

- WOMAC basal.
- Último WOMAC.
- Mejoría WOMAC.
- Fecha de última evaluación.
- Estado: pendiente, vigente o atrasado.

Para evitar saturación, estas columnas podrán mostrarse al filtrar pacientes
con WOMAC activo.

## 11.2 Indicadores agregados

- Pacientes con WOMAC activo.
- Evaluaciones basales completas.
- Evaluaciones de seguimiento pendientes.
- Pacientes con mejoría del WOMAC total.

Estos indicadores son descriptivos y no prueban eficacia terapéutica.

## 11.3 Vista individual

Mostrar:

- Puntaje total basal y actual.
- Mejoría absoluta y porcentual.
- Dolor basal y actual.
- Rigidez basal y actual.
- Función basal y actual.
- Fecha y tipo de cada evaluación.

## 11.4 Gráficos

### Gráfico total

- Eje X: fecha o número de sesión.
- Eje Y: WOMAC total 0–100.
- Menor puntaje representa menor afectación.

### Gráfico de subescalas

Tres líneas:

- Dolor.
- Rigidez.
- Función física.

Todas deben normalizarse a 0–100 para permitir comparación visual.

## 11.5 Relación con otros indicadores

WOMAC se mostrará junto a:

- EVA.
- PGIC.
- Impacto funcional global.
- Consumo de analgésicos.
- Eventos adversos.

No se fusionarán estos valores en una puntuación clínica única.

---

## 12. Informe clínico

El informe incluirá un bloque WOMAC cuando exista al menos una evaluación
completa.

### Contenido

- Versión de WOMAC.
- Fecha basal.
- Puntaje total basal.
- Último puntaje total.
- Mejoría absoluta.
- Mejoría porcentual.
- Subescala dolor basal y actual.
- Subescala rigidez basal y actual.
- Subescala función basal y actual.
- Tipo y fecha de la última evaluación.

### Texto orientativo

> WOMAC [versión] administrado como evaluación basal el [fecha] y repetido el
> [fecha]. Puntaje total basal: [valor]. Último puntaje: [valor]. Cambio
> absoluto: [valor]. Mejoría porcentual: [valor] %. Subescala dolor: [basal] a
> [actual]. Rigidez: [basal] a [actual]. Función física: [basal] a [actual].

### Reglas

- Indicar si los valores son brutos o normalizados.
- No interpretar automáticamente severidad clínica.
- No emitir recomendaciones terapéuticas.
- Señalar evaluaciones incompletas.
- Mantener el informe actual aunque no exista WOMAC.

---

## 13. Exportación CSV

WOMAC debe integrarse con los dos circuitos de exportación definidos para
PROM-ACU.

## 13.1 Exportación clínica interna

Podrá incluir una fila por evaluación:

- `patient_code`
- `womac_assessment_id`
- `assessment_type`
- `assessment_date`
- `session_number`
- `womac_version`
- `response_format`
- `completion_status`
- `pain_raw`
- `pain_normalized`
- `stiffness_raw`
- `stiffness_normalized`
- `function_raw`
- `function_normalized`
- `total_raw`
- `total_normalized`
- `absolute_change_total`
- `percentage_change_total`

Las respuestas individuales podrán exportarse en un archivo clínico separado,
sujeto a permisos.

## 13.2 Exportación científica anonimizada

Podrá incluir:

- `patient_code` o código específico del estudio.
- Grupo etario.
- Sexo.
- Categoría.
- Subcategoría.
- Tipo de evaluación.
- Número de sesión.
- Versión WOMAC.
- Puntajes de subescala.
- Puntaje total.
- Cambios absoluto y porcentual.

No deberá incluir:

- Nombre.
- DNI.
- Teléfono.
- Diagnóstico textual libre.
- Medicación específica.
- Observaciones.
- Respuestas textuales libres.
- Fechas exactas si no son necesarias.

## 13.3 Estructura longitudinal

Se recomienda una fila por evaluación, no una columna nueva por momento. Esto
permite un número variable de seguimientos.

---

## 14. Integración con `patient_code`

## 14.1 Interfaz

La selección de pacientes utilizará únicamente:

> `PAC-000001`

No se mostrará nombre ni DNI en:

- Evaluaciones PROM.
- Dashboard.
- Evolución individual.
- Informes.

## 14.2 Base de datos

Las tablas internas utilizarán `patient_id` como clave foránea. `patient_code`
será el identificador visible y exportable.

Esto evita usar un texto como clave relacional y conserva integridad interna.

## 14.3 Seudonimización

El informe y las exportaciones de investigación utilizarán `patient_code`.

Las respuestas WOMAC también son datos de salud y deben considerarse
potencialmente reidentificables cuando se combinan con otros datos.

---

## 15. Tablas nuevas de SQLite

## 15.1 Tabla `prom_instruments`

Catálogo de instrumentos.

| Campo | Propósito |
|---|---|
| `id` | Identificador |
| `code` | `WOMAC` |
| `name` | Nombre completo |
| `version` | Versión autorizada |
| `language` | Idioma |
| `response_format` | Likert, VAS u otro |
| `license_status` | Estado de autorización |
| `active` | Disponibilidad |
| `created_at` | Fecha de alta |

## 15.2 Tabla `patient_prom_plans`

Define qué PROM está activo para cada paciente.

| Campo | Propósito |
|---|---|
| `id` | Identificador |
| `patient_id` | Paciente |
| `instrument_id` | WOMAC |
| `status` | Sugerido, activo, suspendido o finalizado |
| `interval_sessions` | Frecuencia, por ejemplo 4 |
| `activated_at` | Inicio |
| `deactivated_at` | Finalización |
| `created_at` | Auditoría |

## 15.3 Tabla `prom_assessments`

Cabecera de cada administración.

| Campo | Propósito |
|---|---|
| `id` | Identificador |
| `patient_id` | Paciente |
| `instrument_id` | Instrumento y versión |
| `session_id` | Sesión asociada, si corresponde |
| `assessment_type` | Basal, seguimiento, final o posterior |
| `assessment_date` | Fecha |
| `status` | Pendiente, en progreso, completa, incompleta o anulada |
| `pain_raw` | Dolor bruto |
| `pain_normalized` | Dolor 0–100 |
| `stiffness_raw` | Rigidez bruta |
| `stiffness_normalized` | Rigidez 0–100 |
| `function_raw` | Función bruta |
| `function_normalized` | Función 0–100 |
| `total_raw` | Total bruto |
| `total_normalized` | Total 0–100 |
| `scoring_version` | Versión del algoritmo |
| `completed_at` | Fecha de finalización |
| `created_at` | Auditoría |

## 15.4 Tabla `prom_responses`

Almacena respuestas individuales.

| Campo | Propósito |
|---|---|
| `id` | Identificador |
| `assessment_id` | Evaluación |
| `item_code` | Código estable del ítem |
| `subscale` | Dolor, rigidez o función |
| `item_order` | Orden oficial |
| `response_value` | Valor numérico |
| `is_missing` | Respuesta faltante |
| `created_at` | Auditoría |

El texto del ítem no necesita duplicarse si existe un catálogo autorizado y
versionado.

## 15.5 Tabla opcional `prom_items`

Catálogo de ítems por versión.

| Campo | Propósito |
|---|---|
| `id` | Identificador |
| `instrument_id` | Versión WOMAC |
| `item_code` | Código |
| `subscale` | Subescala |
| `item_order` | Posición |
| `item_text` | Texto autorizado |
| `active` | Vigencia |

Su uso dependerá de las condiciones de licencia para almacenar y distribuir el
texto.

---

## 16. Reglas de integridad

- Solo una evaluación basal válida por plan WOMAC.
- Una evaluación debe estar asociada a una versión.
- Todas las respuestas deben pertenecer a esa versión.
- Los valores deben estar dentro del rango permitido.
- Los puntajes deben recalcularse desde las respuestas.
- No permitir edición silenciosa después de cerrar una evaluación.
- Una corrección debe quedar auditada.
- No comparar versiones incompatibles.
- No borrar evaluaciones históricas.
- Las evaluaciones anuladas deben conservarse sin participar en cálculos.

---

## 17. Alertas operativas

- WOMAC basal pendiente.
- Seguimiento vencido.
- Evaluación incompleta.
- Respuesta fuera de rango.
- Dos evaluaciones basales activas.
- Cambio de versión durante el seguimiento.
- Evaluación final pendiente al cerrar tratamiento.

Estas alertas son de calidad de datos y seguimiento. No constituyen alertas
diagnósticas.

---

## 18. Qué no debe romper

La incorporación de WOMAC no debe alterar:

### EVA

- Definición basal.
- Cálculo absoluto.
- Cálculo porcentual.
- Clasificación de respuesta actual.
- Gráfico existente.

### PGIC

- Pregunta.
- Opciones 1–7.
- Historial.
- Indicador agregado.

### Impacto funcional global

- Escala 0–10.
- Registro por sesión.
- Gráfico.
- Informe.

### Dashboard actual

- Indicadores existentes.
- Modo seudonimizado.
- Evolución individual.
- Exportaciones existentes.

### Informes actuales

- Generación TXT.
- Información clínica vigente.
- Variante seudonimizada.
- Omisión de identificadores directos.

### Seudonimización

- Uso visible de `patient_code`.
- Ausencia de nombre, DNI y teléfono fuera del alta del paciente.
- Exportaciones gobernadas por finalidad.

---

## 19. Alcance de primera implementación

La primera versión de WOMAC debería incluir:

- Activación manual para un paciente elegible.
- Evaluación basal.
- Seguimiento cada 4 sesiones.
- Evaluación final.
- Formulario completo de la versión autorizada.
- Cálculo de subescalas y total.
- Normalización 0–100.
- Comparación con basal.
- Dashboard individual.
- Informe clínico.
- Exportación estructurada.

No debería incluir todavía:

- Interpretación automática de severidad.
- Recomendaciones terapéuticas.
- IA.
- Portal remoto del paciente.
- Notificaciones externas.
- Comparación automática con valores poblacionales.

---

## 20. Plan de implementación

### Fase 1: validación clínica y legal

1. Seleccionar versión WOMAC.
2. Confirmar licencia.
3. Confirmar traducción.
4. Validar reglas de puntuación.
5. Definir manejo de datos faltantes.

### Fase 2: modelo de datos

1. Crear catálogo del instrumento.
2. Crear planes PROM.
3. Crear evaluaciones.
4. Crear respuestas.
5. Definir auditoría.

### Fase 3: formulario

1. Implementar instrucciones.
2. Implementar 24 ítems autorizados.
3. Incorporar validaciones.
4. Añadir revisión final.
5. Guardar borradores.

### Fase 4: puntuación

1. Calcular subescalas.
2. Calcular total.
3. Normalizar.
4. Comparar con basal.
5. Validar con casos oficiales.

### Fase 5: visualización

1. Dashboard.
2. Gráficos.
3. Informe.
4. Exportaciones.

### Fase 6: validación

1. Pruebas unitarias.
2. Pruebas con casos de referencia.
3. Revisión clínica.
4. Pruebas de usabilidad.
5. Control de seudonimización.

---

## 21. Criterios de aceptación

WOMAC estará correctamente implementado cuando:

- La versión y licencia estén documentadas.
- Los 24 ítems correspondan a la versión autorizada.
- Las subescalas tengan 5, 2 y 17 ítems.
- Los cálculos coincidan con casos de referencia.
- El puntaje total esté claramente identificado.
- Se diferencien valores brutos y normalizados.
- La basal sea explícita.
- La periodicidad sea configurable.
- Los datos faltantes no se conviertan en cero.
- Dashboard, informe y CSV muestren resultados consistentes.
- El paciente se identifique mediante `patient_code`.
- EVA, PGIC e impacto funcional continúen funcionando sin cambios.
- La app no emita diagnósticos ni recomendaciones terapéuticas.

---

## 22. Decisión recomendada

PROM-ACU debe implementar WOMAC como un módulo PROM versionado y separado de las
sesiones clínicas, relacionado con ellas mediante claves foráneas.

La recomendación inicial es:

- Utilizar una versión oficialmente autorizada.
- Aplicar basal, cada 4 sesiones y al cierre.
- Guardar respuestas individuales y resultados calculados.
- Mostrar puntajes brutos y normalizados.
- Comparar siempre contra una basal explícita de la misma versión.
- Mantener WOMAC como complemento, no sustituto, de EVA, PGIC e impacto
  funcional global.

La programación no debe comenzar hasta cerrar la versión, licencia, traducción
y reglas oficiales de puntuación.
