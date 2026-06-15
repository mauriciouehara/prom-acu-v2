# GOBERNANZA DE EXPORTACIONES DE PROM-ACU

## 1. Propósito

Este documento define la separación de las exportaciones de PROM-ACU en dos
productos de datos con finalidades y niveles de protección diferentes:

1. **Exportación clínica interna**
2. **Exportación científica anonimizada**

La separación busca aplicar el principio de minimización de datos: cada
exportación debe contener solamente la información necesaria para su finalidad.

> La seudonimización y la eliminación de identificadores directos reducen el
> riesgo de identificación, pero no garantizan por sí solas una anonimización
> irreversible.

---

## 2. Situación actual

El CSV seudonimizado actual exporta:

- `patient_code`
- Edad
- Sexo
- Diagnóstico textual
- Categoría clínica
- Subcategoría
- PROM sugerido
- Número de sesión
- EVA pre
- EVA post
- PGIC
- Impacto funcional global
- Nombre de la medicación
- Frecuencia de la medicación
- Cambio en el consumo de analgésicos
- Severidad del evento adverso
- Indicador histórico de evento adverso

No incluye nombre, DNI ni teléfono. Sin embargo, el diagnóstico textual, la
medicación específica y la combinación de variables longitudinales pueden
facilitar la reidentificación.

Por esa razón, el CSV actual debe evolucionar hacia dos exportaciones separadas.

---

## 3. Exportación clínica interna

## 3.1 Finalidad

La exportación clínica interna está destinada a:

- Auditoría clínica.
- Continuidad asistencial.
- Revisión profesional.
- Control de calidad.
- Gestión interna autorizada.
- Análisis clínico dentro de la institución.

No debe utilizarse como archivo científico anonimizado ni compartirse fuera del
entorno clínico autorizado sin una evaluación adicional.

## 3.2 Identificación

Utilizará `patient_code` como identificador operativo.

No necesita incluir nombre, DNI ni teléfono en el diseño propuesto, aunque la
institución conserva esos datos en la base clínica principal.

## 3.3 Columnas propuestas

| Columna | Descripción |
|---|---|
| `patient_code` | Código seudonimizado del paciente |
| `age` | Edad registrada |
| `sex` | Sexo registrado |
| `diagnosis` | Diagnóstico clínico textual |
| `clinical_category` | Categoría clínica |
| `clinical_subcategory` | Subcategoría |
| `suggested_prom` | PROM sugerido |
| `session_number` | Número de sesión |
| `session_date` | Fecha de la sesión, si el uso interno lo requiere |
| `eva_pre` | EVA previa a la sesión |
| `eva_post` | EVA posterior a la sesión |
| `pgic` | Patient Global Impression of Change |
| `functional_impact` | Impacto funcional global |
| `medication_name` | Medicación relevante actual |
| `medication_frequency` | Frecuencia de uso |
| `analgesic_change` | Cambio de analgésicos respecto del inicio |
| `adverse_event_severity` | Severidad del evento adverso |
| `adverse_event_description` | Descripción libre, solo si está autorizada |

### Observaciones

- La descripción libre del evento adverso puede contener identificadores
  escritos manualmente.
- Su inclusión debe ser opcional y restringida.
- Las observaciones clínicas libres no deberían exportarse por defecto.
- El archivo debe tratarse como información clínica sensible.

## 3.4 Riesgo de reidentificación

**Riesgo estimado: Alto.**

Aunque no incluya identificadores directos, contiene:

- Diagnóstico textual.
- Edad exacta.
- Medicación específica.
- Frecuencia de medicación.
- Posibles descripciones libres.
- Trayectoria clínica longitudinal.

La combinación de esos datos puede permitir identificar a una persona mediante
información externa.

## 3.5 Controles recomendados

- Acceso exclusivo para personal autorizado.
- Registro de quién genera y descarga el archivo.
- Justificación o finalidad de la exportación.
- Almacenamiento cifrado.
- Prohibición de envío por canales no autorizados.
- Caducidad o política de eliminación.
- Advertencia visible sobre datos clínicos sensibles.

---

## 4. Exportación científica anonimizada

## 4.1 Finalidad

La exportación científica anonimizada está destinada a:

- Análisis estadístico.
- Preparación de conjuntos de investigación.
- Estudios observacionales.
- Evaluación agregada de resultados.
- Intercambio controlado con equipos científicos autorizados.

Debe aplicar una minimización mayor que la exportación clínica.

## 4.2 Datos expresamente excluidos

La exportación científica no debe incluir:

- Nombre.
- DNI.
- Teléfono.
- Diagnóstico textual libre.
- Medicación específica.
- Frecuencia textual de medicación.
- Observaciones clínicas libres.
- Descripción libre de eventos adversos.
- Fecha exacta de sesión.
- Cualquier texto libre no revisado.

## 4.3 Columnas propuestas

| Columna | Descripción |
|---|---|
| `patient_code` | Código del paciente para vincular sesiones dentro del conjunto |
| `age_group` | Grupo etario, no edad exacta |
| `sex` | Sexo registrado |
| `clinical_category` | Categoría clínica |
| `clinical_subcategory` | Subcategoría |
| `suggested_prom` | PROM sugerido |
| `session_number` | Número ordinal de sesión |
| `eva_pre` | EVA previa |
| `eva_post` | EVA posterior |
| `pgic` | PGIC |
| `functional_impact` | Impacto funcional global |
| `adverse_event_severity` | Ninguno, leve, moderado o severo |

## 4.4 Grupos etarios

La edad exacta se transformará en un grupo etario.

Propuesta inicial:

| Grupo | Rango |
|---|---|
| `18-29` | 18 a 29 años |
| `30-39` | 30 a 39 años |
| `40-49` | 40 a 49 años |
| `50-59` | 50 a 59 años |
| `60-69` | 60 a 69 años |
| `70-79` | 70 a 79 años |
| `80+` | 80 años o más |
| `Menor de 18` | Solo si el sistema admite esa población |
| `Sin dato` | Edad no disponible |

Los grupos podrán ampliarse cuando existan pocos participantes en una categoría
y sea necesario reducir el riesgo de singularidad.

## 4.5 Uso de `patient_code`

El código permite relacionar varias sesiones del mismo paciente sin incluir
identificadores directos.

Sin embargo, `patient_code` sigue siendo un seudónimo estable. Si una persona
tiene acceso a la base clínica, podría relacionarlo con su identidad.

Por ello, esta exportación es técnicamente **seudonimizada y minimizada**, no
necesariamente anónima de forma irreversible.

Para estudios externos de mayor exigencia podría reemplazarse por un código
específico del estudio, generado mediante una tabla de correspondencia separada.

## 4.6 Riesgo de reidentificación

**Riesgo estimado: Bajo a medio.**

El riesgo disminuye porque se eliminan:

- Identificadores directos.
- Edad exacta.
- Diagnóstico libre.
- Medicación específica.
- Fechas exactas.
- Textos libres.

El riesgo no es cero debido a:

- Subcategorías poco frecuentes.
- Combinaciones clínicas singulares.
- Secuencias longitudinales.
- Eventos adversos raros.
- Persistencia de un código estable.
- Tamaño reducido de algunos grupos.

Antes de compartir un conjunto, deberá evaluarse la cantidad de personas por
combinación de grupo etario, sexo, categoría y subcategoría.

---

## 5. Qué cambia respecto del CSV actual

## 5.1 El CSV actual deja de ser una única exportación

Será sustituido por:

- **CSV clínico interno**
- **CSV científico anonimizado**

## 5.2 Cambios en la exportación clínica

La exportación clínica conservará los datos detallados necesarios para uso
asistencial interno:

- Diagnóstico textual.
- Edad exacta.
- Medicación.
- Frecuencia.
- Evolución clínica.

Deberá presentarse como archivo sensible y no como archivo anonimizado.

## 5.3 Cambios en la exportación científica

Se eliminarán:

- `diagnosis`
- `age`
- `medication_name`
- `medication_frequency`
- Cualquier campo libre
- Fecha exacta, si estuviera incluida

Se incorporará:

- `age_group`

Se conservarán únicamente variables estructuradas necesarias para análisis.

## 5.4 Eventos adversos

La exportación científica incluirá solamente:

- `adverse_event_severity`

No incluirá:

- Descripción libre.
- Notas clínicas.
- Indicadores históricos redundantes.

---

## 6. Comparación de columnas

| Variable | Clínica interna | Científica anonimizada |
|---|---:|---:|
| `patient_code` | Sí | Sí |
| Nombre | No por defecto | No |
| DNI | No | No |
| Teléfono | No | No |
| Edad exacta | Sí | No |
| Grupo etario | Opcional | Sí |
| Sexo | Sí | Sí |
| Diagnóstico textual | Sí | No |
| Categoría | Sí | Sí |
| Subcategoría | Sí | Sí |
| PROM sugerido | Sí | Sí |
| Número de sesión | Sí | Sí |
| Fecha de sesión | Opcional | No |
| EVA pre | Sí | Sí |
| EVA post | Sí | Sí |
| PGIC | Sí | Sí |
| Impacto funcional | Sí | Sí |
| Medicación específica | Sí | No |
| Frecuencia de medicación | Sí | No |
| Cambio de analgésicos | Sí | No en el alcance solicitado |
| Severidad del evento adverso | Sí | Sí |
| Descripción del evento adverso | Opcional y restringida | No |
| Observaciones clínicas | No por defecto | No |

---

## 7. Diseño de interfaz

## 7.1 Ubicación

En el Dashboard médico se mostrará una sección:

> **Exportaciones de datos**

La sección tendrá dos tarjetas o bloques separados.

## 7.2 Tarjeta de exportación clínica interna

Título:

> Exportación clínica interna

Descripción:

> Contiene información clínica detallada, incluyendo diagnóstico y medicación.
> Uso exclusivo de personal autorizado.

Advertencia:

> Este archivo contiene datos clínicos sensibles y presenta alto riesgo de
> reidentificación.

Acción:

> Descargar CSV clínico interno

Se recomienda una confirmación previa a la descarga.

## 7.3 Tarjeta de exportación científica

Título:

> Exportación científica anonimizada

Descripción:

> Excluye identificadores directos, diagnóstico libre, medicación específica y
> textos libres. La edad se presenta por grupos.

Advertencia:

> Los datos seudonimizados y minimizados reducen el riesgo de identificación,
> pero no equivalen necesariamente a anonimización irreversible.

Acción:

> Descargar CSV científico

## 7.4 Resumen previo

Antes de descargar, la interfaz mostrará:

- Número de pacientes.
- Número de sesiones.
- Columnas incluidas.
- Columnas excluidas.
- Nivel estimado de riesgo.
- Fecha de generación.

## 7.5 Nombres de archivos

Propuesta:

- `prom_acu_exportacion_clinica_YYYY-MM-DD.csv`
- `prom_acu_exportacion_cientifica_YYYY-MM-DD.csv`

## 7.6 Modo investigación del Dashboard

El modo investigación seguirá ocultando nombre, DNI y teléfono en pantalla.

La disponibilidad de la exportación clínica no dependerá de ese interruptor.
Cada botón deberá mantener su propia finalidad y advertencia para evitar
confundir la visualización seudonimizada con una exportación anónima.

---

## 8. Matriz de riesgos

| Exportación | Riesgo | Motivo principal |
|---|---|---|
| Clínica interna | Alto | Diagnóstico, edad exacta, medicación y datos longitudinales |
| Científica anonimizada | Bajo a medio | Código persistente y combinaciones clínicas potencialmente singulares |

El nivel real dependerá también de:

- Tamaño del conjunto.
- Frecuencia de cada subcategoría.
- Acceso a fuentes externas.
- Contexto institucional.
- Forma de almacenamiento y transferencia.

---

## 9. Controles de gobernanza recomendados

### Para ambas exportaciones

- Registrar fecha y hora.
- Registrar usuario responsable.
- Registrar finalidad.
- Aplicar control de acceso.
- Proteger archivos en reposo y tránsito.
- Definir período de conservación.
- Evitar almacenamiento en dispositivos personales.

### Para la exportación clínica

- Acceso más restrictivo.
- Confirmación antes de descargar.
- Justificación obligatoria.
- Auditoría de descargas.
- Prohibición de uso científico externo sin transformación adicional.

### Para la exportación científica

- Evaluar celdas pequeñas o combinaciones únicas.
- Agrupar categorías poco frecuentes cuando sea necesario.
- Considerar códigos específicos por estudio.
- Documentar el diccionario de datos.
- Registrar la versión de las reglas de anonimización.

---

## 10. Criterios de aceptación

La mejora estará correctamente diseñada cuando:

- Existan dos exportaciones claramente diferenciadas.
- La exportación clínica se identifique como sensible.
- La exportación científica no contenga identificadores directos.
- La exportación científica no contenga diagnóstico libre.
- La exportación científica no contenga medicación específica.
- La edad exacta sea reemplazada por grupo etario.
- No se exporten textos libres en el conjunto científico.
- La interfaz explique finalidad y riesgo antes de descargar.
- El modo investigación no se confunda con anonimización irreversible.
- Ambas estructuras estén documentadas y sean auditables.

---

## 11. Decisión de gobernanza

PROM-ACU adoptará dos circuitos separados:

### Circuito clínico interno

Datos detallados, seudonimizados mediante `patient_code`, para uso profesional
autorizado. Riesgo de reidentificación alto.

### Circuito científico anonimizado

Datos minimizados y estructurados, sin diagnóstico textual, medicación
específica, edad exacta ni campos libres. Riesgo de reidentificación bajo a
medio, sujeto a evaluación del conjunto antes de compartirlo.

Esta separación evita presentar un archivo clínico detallado como si fuera
anónimo y permite que cada uso de datos tenga controles proporcionales a su
finalidad.
