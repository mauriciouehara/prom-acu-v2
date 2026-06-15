# CAPA 2: CLASIFICACIÓN CLÍNICA DEL PACIENTE

## 1. Propósito

La CAPA 2 incorpora una clasificación clínica estructurada para que cada
paciente de PROM-ACU quede asociado a:

1. Una **categoría principal**.
2. Una **subcategoría diagnóstica**.

Esta clasificación permitirá ordenar la población atendida, mejorar la
visualización del dashboard, facilitar análisis clínicos y de investigación, y
activar PROMs específicos en futuras versiones.

La clasificación no reemplaza el campo actual de diagnóstico médico. Tampoco
debe utilizarse para inferir, confirmar o inventar diagnósticos.

> PROM-ACU registra una clasificación seleccionada y confirmada por un
> profesional. No diagnostica ni recomienda tratamientos.

---

## 2. Situación actual de PROM-ACU

La aplicación existente registra:

- Diagnóstico médico principal como texto libre.
- Motivo principal mediante una lista cerrada.
- Escala asignada mediante una regla fija basada en ese motivo.

Los motivos actuales son:

- Rodilla.
- Cadera.
- Lumbalgia.
- Cervicalgia.
- Hombro.
- Dolor general.
- Estrés / ansiedad.
- Insomnio.
- Digestivo funcional.
- Respiratorio funcional.

Este modelo es suficiente para un prototipo, pero mezcla tres conceptos:

- Región o sistema corporal.
- Síntoma principal.
- Diagnóstico clínico.

La CAPA 2 debe separar esos conceptos sin eliminar los datos existentes.

---

## 3. Principios de diseño

### 3.1 Clasificación jerárquica

Cada paciente tendrá una categoría amplia y una subcategoría más específica.
La subcategoría dependerá de la categoría elegida.

### 3.2 Diagnóstico conservado

El diagnóstico médico principal seguirá existiendo como texto libre y deberá
representar únicamente información ya documentada por un profesional.

### 3.3 Selección profesional

La aplicación puede sugerir opciones o PROMs, pero la categoría y la
subcategoría deben ser seleccionadas o confirmadas por un profesional.

### 3.4 Catálogo controlado

Las categorías y subcategorías deben almacenarse con identificadores estables.
Los nombres visibles podrán actualizarse sin alterar registros históricos.

### 3.5 Extensibilidad

El diseño debe permitir:

- Incorporar nuevas subcategorías.
- Desactivar opciones sin borrar registros anteriores.
- Versionar la clasificación.
- Asociar varios PROMs a una categoría o subcategoría.
- Definir PROMs obligatorios, recomendados u opcionales.

### 3.6 No confundir clasificación con respuesta clínica

La clasificación clínica del paciente describe el problema seguido. Es
independiente de la clasificación de respuesta basada en EVA, como “Moderada”
o “Muy buena respuesta”.

---

## 4. Modelo conceptual

### Categoría principal

Agrupación clínica amplia que representa el sistema, región o dominio principal
del seguimiento.

Ejemplo:

> Musculoesquelético > Columna lumbar

### Subcategoría diagnóstica

Clasificación más específica dentro de la categoría. Puede representar una
región anatómica, un síndrome clínico o un diagnóstico médico documentado.

Ejemplo:

> Musculoesquelético > Columna lumbar > Lumbalgia inespecífica

### Diagnóstico médico principal

Texto libre que conserva la denominación documentada por el profesional.

Ejemplo:

> Lumbalgia mecánica crónica sin signos radiculares.

### Motivo principal histórico

Campo actualmente utilizado por PROM-ACU. Durante la transición se conservará
para compatibilidad, pero dejará de ser la fuente principal de clasificación.

---

## 5. Estructura propuesta de categorías

Se propone comenzar con seis categorías activas y una categoría operativa de
excepción.

| Código | Categoría principal | Alcance |
|---|---|---|
| MSK | Musculoesquelético | Dolor y limitación funcional regional |
| PAIN | Dolor general o persistente | Dolor no limitado a una única región |
| MENTAL | Bienestar emocional | Estrés, ansiedad y síntomas emocionales en seguimiento |
| SLEEP | Sueño | Insomnio y alteraciones del sueño |
| GI | Digestivo funcional | Síntomas gastrointestinales funcionales documentados |
| RESP | Respiratorio funcional | Seguimiento funcional respiratorio documentado |
| OTHER | Otra categoría / pendiente de clasificación | Casos aún no incluidos o pendientes de confirmación |

### Reglas de uso

- Solo una categoría podrá marcarse como principal en la primera versión.
- “Otra categoría” no debe utilizarse para ocultar una clasificación conocida.
- “Pendiente de clasificación” debe diferenciarse de “Otra categoría”.
- Las categorías deben poder activarse o desactivarse administrativamente.
- Los códigos internos no deben depender del texto visible.

---

## 6. Estructura propuesta de subcategorías

## 6.1 Musculoesquelético

| Código | Subcategoría | Observación |
|---|---|---|
| MSK_KNEE | Rodilla | Clasificación regional general |
| MSK_KNEE_OA | Artrosis de rodilla | Solo con diagnóstico documentado |
| MSK_KNEE_OTHER | Otra condición de rodilla | Requiere diagnóstico libre |
| MSK_HIP | Cadera | Clasificación regional general |
| MSK_HIP_OA | Artrosis de cadera | Solo con diagnóstico documentado |
| MSK_HIP_OTHER | Otra condición de cadera | Requiere diagnóstico libre |
| MSK_LUMBAR | Columna lumbar / lumbalgia | Clasificación regional general |
| MSK_LUMBAR_NONSPECIFIC | Lumbalgia inespecífica | Solo si está documentada |
| MSK_LUMBAR_RADICULAR | Dolor lumbar con componente radicular documentado | No inferir por síntomas aislados |
| MSK_LUMBAR_OTHER | Otra condición lumbar | Requiere diagnóstico libre |
| MSK_CERVICAL | Columna cervical / cervicalgia | Clasificación regional general |
| MSK_CERVICAL_NONSPECIFIC | Cervicalgia inespecífica | Solo si está documentada |
| MSK_CERVICAL_RADICULAR | Dolor cervical con componente radicular documentado | No inferir automáticamente |
| MSK_CERVICAL_OTHER | Otra condición cervical | Requiere diagnóstico libre |
| MSK_SHOULDER | Hombro | Clasificación regional general |
| MSK_SHOULDER_RCRSP | Dolor de hombro relacionado con manguito rotador | Solo con documentación clínica |
| MSK_SHOULDER_ADHESIVE | Capsulitis adhesiva | Solo con diagnóstico documentado |
| MSK_SHOULDER_OTHER | Otra condición de hombro | Requiere diagnóstico libre |
| MSK_ELBOW | Codo | Preparado para expansión |
| MSK_HAND_WRIST | Mano / muñeca | Preparado para expansión |
| MSK_ANKLE_FOOT | Tobillo / pie | Preparado para expansión |
| MSK_MULTIREGIONAL | Dolor musculoesquelético multirregional | Más de una región relevante |
| MSK_OTHER | Otra condición musculoesquelética | Requiere diagnóstico libre |

### Criterio UX

La primera versión puede mostrar inicialmente las regiones ya soportadas:
rodilla, cadera, lumbar, cervical y hombro. Las demás pueden permanecer
inactivas hasta contar con PROMs y flujos definidos.

## 6.2 Dolor general o persistente

| Código | Subcategoría | Observación |
|---|---|---|
| PAIN_GENERAL | Dolor general | Sin localización única predominante |
| PAIN_PERSISTENT | Dolor persistente | Utilizar según definición clínica adoptada |
| PAIN_WIDESPREAD | Dolor generalizado | Solo si está documentado |
| PAIN_NEUROPATHIC | Dolor neuropático documentado | No inferir mediante la app |
| PAIN_OTHER | Otro cuadro de dolor | Requiere diagnóstico libre |

## 6.3 Bienestar emocional

| Código | Subcategoría | Observación |
|---|---|---|
| MENTAL_STRESS | Estrés percibido | Seguimiento de síntomas, no diagnóstico |
| MENTAL_ANXIETY_SYMPTOMS | Síntomas de ansiedad | No equivale a trastorno diagnosticado |
| MENTAL_ANXIETY_DIAGNOSED | Trastorno de ansiedad documentado | Solo con diagnóstico previo |
| MENTAL_MIXED | Estrés y síntomas de ansiedad | Seguimiento combinado |
| MENTAL_OTHER | Otro motivo de bienestar emocional | Requiere descripción |

La aplicación debe distinguir expresamente “síntomas de ansiedad” de un
“trastorno de ansiedad documentado”.

## 6.4 Sueño

| Código | Subcategoría | Observación |
|---|---|---|
| SLEEP_INSOMNIA_SYMPTOMS | Síntomas de insomnio | Sin asumir diagnóstico |
| SLEEP_INSOMNIA_DIAGNOSED | Trastorno de insomnio documentado | Solo con diagnóstico previo |
| SLEEP_MAINTENANCE | Dificultad para mantener el sueño | Seguimiento sintomático |
| SLEEP_ONSET | Dificultad para iniciar el sueño | Seguimiento sintomático |
| SLEEP_OTHER | Otra alteración del sueño | Requiere descripción |

## 6.5 Digestivo funcional

| Código | Subcategoría | Observación |
|---|---|---|
| GI_IBS | Síndrome de intestino irritable documentado | Asociable a IBS-SSS |
| GI_DYSPEPSIA | Dispepsia funcional documentada | PROM específico pendiente |
| GI_FUNCTIONAL_SYMPTOMS | Síntomas digestivos funcionales | Sin diagnóstico específico |
| GI_OTHER | Otro cuadro digestivo funcional | Requiere descripción |

La categoría no debe utilizarse para retrasar evaluación médica ante síntomas
de alarma.

## 6.6 Respiratorio funcional

| Código | Subcategoría | Observación |
|---|---|---|
| RESP_ASTHMA | Asma documentada | Asociable a ACT |
| RESP_COPD | EPOC documentada | Asociable a CAT |
| RESP_FUNCTIONAL_SYMPTOMS | Síntomas respiratorios funcionales | Sin diagnóstico específico |
| RESP_OTHER | Otro cuadro respiratorio | Requiere descripción |

ACT y CAT no son intercambiables: la selección dependerá del diagnóstico
documentado y de las condiciones de uso del instrumento.

## 6.7 Otra categoría o pendiente

| Código | Subcategoría | Uso |
|---|---|---|
| OTHER_NOT_LISTED | Condición no incluida | Exige descripción clínica |
| OTHER_PENDING | Pendiente de clasificación | Uso temporal |

“Pendiente de clasificación” no activará automáticamente PROMs específicos.

---

## 7. Reglas de clasificación

1. La categoría principal será obligatoria para pacientes nuevos.
2. La subcategoría será obligatoria, excepto durante una migración controlada.
3. Las subcategorías disponibles dependerán de la categoría seleccionada.
4. El diagnóstico médico principal seguirá siendo un campo independiente.
5. La app no derivará automáticamente una subcategoría desde el diagnóstico
   libre.
6. Una sugerencia futura mediante IA deberá ser confirmada por un profesional.
7. Las opciones que representen un diagnóstico específico deberán indicar
   “documentado” en su etiqueta o ayuda contextual.
8. No se permitirá una combinación categoría-subcategoría inválida.
9. Los cambios de clasificación no modificarán sesiones ni resultados previos.
10. En investigación deberá conservarse qué clasificación estaba vigente en
    cada período.

---

## 8. Diseño UX en Registro de Paciente

## 8.1 Orden de campos

Se propone organizar el formulario en tres bloques.

### Bloque A: identificación

- Nombre y apellido.
- DNI.
- Edad.
- Sexo.
- Teléfono.

### Bloque B: clasificación clínica

1. **Categoría principal**
2. **Subcategoría diagnóstica**
3. **Diagnóstico médico principal registrado**
4. **Detalle clínico opcional**

### Bloque C: instrumentos de seguimiento

- PROMs sugeridos.
- PROMs seleccionados por el profesional.
- Instrumentos pendientes de implementación.

## 8.2 Comportamiento de los controles

### Categoría principal

Control de selección única con lenguaje claro.

Ejemplo:

> Categoría principal: Musculoesquelético

### Subcategoría diagnóstica

Lista dependiente de la categoría seleccionada.

Ejemplo:

> Subcategoría: Columna lumbar / lumbalgia

Al cambiar la categoría, la aplicación debe limpiar cualquier subcategoría
incompatible y solicitar una nueva selección.

### Diagnóstico médico principal

Campo libre conservado, acompañado por la aclaración:

> Registre únicamente un diagnóstico previamente documentado. PROM-ACU no
> emite diagnósticos.

### PROMs sugeridos

Panel informativo posterior a la clasificación:

> Seguimiento general: EVA y PGIC  
> PROM específico sugerido: ODI  
> Estado: pendiente de implementación

La sugerencia no debe guardarse como instrumento administrado hasta que el
profesional la confirme.

## 8.3 Casos especiales

### Subcategoría general

Si no existe un diagnóstico específico documentado, el profesional podrá
elegir una subcategoría regional general, como “Rodilla”.

### Otra condición

Al elegir “Otra condición”, el detalle clínico será obligatorio.

### Pendiente de clasificación

Debe mostrar una advertencia no bloqueante:

> Clasificación pendiente. Solo se activarán los instrumentos generales hasta
> que un profesional complete la clasificación.

## 8.4 Resumen antes de guardar

Antes de confirmar el alta, se mostrará:

- Categoría.
- Subcategoría.
- Diagnóstico registrado.
- PROMs sugeridos.

Esto reduce errores de clasificación sin agregar pasos innecesarios.

---

## 9. Visualización en Dashboard

## 9.1 Tabla general

Agregar columnas:

- Categoría principal.
- Subcategoría.
- Diagnóstico registrado.
- PROMs activos.

Orden sugerido:

1. Paciente.
2. Categoría.
3. Subcategoría.
4. Diagnóstico.
5. EVA basal.
6. Última EVA.
7. Último PGIC.
8. Mejoría.
9. Sesiones.
10. Estado clínico.

En pantallas pequeñas, categoría y subcategoría pueden mostrarse en una sola
columna:

> Musculoesquelético · Rodilla

## 9.2 Filtros

El dashboard deberá permitir filtrar por:

- Categoría principal.
- Subcategoría.
- PROM activo.
- Estado de clasificación.
- Estado clínico de evolución.

La lista de subcategorías del filtro dependerá de la categoría seleccionada.

## 9.3 Resumen poblacional

Indicadores propuestos:

- Pacientes por categoría.
- Pacientes por subcategoría.
- Pacientes pendientes de clasificación.
- Pacientes con PROM específico activo.
- Pacientes sin PROM específico disponible.

Estos indicadores son descriptivos y no deben presentarse como resultados de
efectividad sin un diseño de investigación adecuado.

## 9.4 Vista individual

Encabezado recomendado:

> Categoría: Musculoesquelético  
> Subcategoría: Artrosis de rodilla  
> Diagnóstico registrado: Gonartrosis derecha  
> PROMs activos: EVA, PGIC, WOMAC

La clasificación debe aparecer cerca de la identidad del paciente, no mezclada
con la respuesta clínica calculada.

---

## 10. Almacenamiento en SQLite

Se recomienda un modelo normalizado en lugar de guardar solamente textos en la
tabla `patients`.

## 10.1 Tabla `clinical_categories`

Catálogo de categorías principales.

| Campo | Propósito |
|---|---|
| id | Identificador interno |
| code | Código estable y único, por ejemplo `MSK` |
| name | Nombre visible |
| description | Definición funcional |
| active | Permite ocultar sin borrar |
| sort_order | Orden de presentación |
| version | Versión del catálogo |
| created_at | Fecha de creación |
| updated_at | Última modificación |

## 10.2 Tabla `clinical_subcategories`

Catálogo de subcategorías.

| Campo | Propósito |
|---|---|
| id | Identificador interno |
| category_id | Categoría a la que pertenece |
| code | Código estable y único |
| name | Nombre visible |
| description | Definición y criterio de uso |
| requires_documented_diagnosis | Indica si exige diagnóstico previo |
| requires_detail | Indica si exige texto adicional |
| active | Permite desactivar sin borrar |
| sort_order | Orden de presentación |
| version | Versión del catálogo |
| created_at | Fecha de creación |
| updated_at | Última modificación |

Debe existir una restricción que impida asociar una subcategoría con una
categoría incorrecta.

## 10.3 Clasificación vigente del paciente

Para una primera implementación simple, `patients` puede incorporar:

| Campo | Propósito |
|---|---|
| category_id | Categoría principal vigente |
| subcategory_id | Subcategoría vigente |
| classification_detail | Detalle cuando corresponda |
| classified_at | Fecha de clasificación |
| classification_status | Confirmada, pendiente o histórica migrada |

El campo `diagnosis` actual se conserva.

## 10.4 Historial de clasificaciones

Para investigación y trazabilidad se recomienda una tabla
`patient_classifications`.

| Campo | Propósito |
|---|---|
| id | Identificador |
| patient_id | Paciente |
| category_id | Categoría |
| subcategory_id | Subcategoría |
| diagnosis_snapshot | Diagnóstico registrado en ese momento |
| detail | Aclaración clínica |
| valid_from | Inicio de vigencia |
| valid_to | Fin de vigencia, si corresponde |
| is_current | Clasificación vigente |
| source | Manual, migración o sugerencia confirmada |
| confirmed_by | Profesional que confirmó |
| created_at | Fecha de registro |

Esta tabla evita sobrescribir la historia cuando cambia el problema principal.

## 10.5 Integridad y eliminación

- Las categorías utilizadas no deben eliminarse físicamente.
- Una opción obsoleta se marcará como inactiva.
- Los registros históricos conservarán sus identificadores.
- El nombre visible podrá cambiar, pero el código permanecerá estable.
- La base deberá impedir subcategorías pertenecientes a otra categoría.
- Un paciente no deberá tener más de una clasificación principal vigente.

---

## 11. Migración desde el modelo actual

La migración no debe borrar ni reemplazar `diagnosis`, `main_complaint` o
`assigned_scale`.

### Mapeo inicial sugerido

| Motivo actual | Categoría | Subcategoría inicial |
|---|---|---|
| Rodilla | Musculoesquelético | Rodilla |
| Cadera | Musculoesquelético | Cadera |
| Lumbalgia | Musculoesquelético | Columna lumbar / lumbalgia |
| Cervicalgia | Musculoesquelético | Columna cervical / cervicalgia |
| Hombro | Musculoesquelético | Hombro |
| Dolor general | Dolor general o persistente | Dolor general |
| Estrés / ansiedad | Bienestar emocional | Estrés y síntomas de ansiedad |
| Insomnio | Sueño | Síntomas de insomnio |
| Digestivo funcional | Digestivo funcional | Síntomas digestivos funcionales |
| Respiratorio funcional | Respiratorio funcional | Síntomas respiratorios funcionales |

### Estado de los datos migrados

Las clasificaciones creadas automáticamente deberán marcarse como:

> Histórica migrada, pendiente de confirmación profesional.

El sistema no debe transformar un motivo amplio en un diagnóstico específico.
Por ejemplo, “Rodilla” no debe convertirse automáticamente en “Artrosis de
rodilla”.

---

## 12. Activación futura de PROMs

La clasificación debe alimentar un motor de reglas configurable, no una cadena
de condiciones fija dentro de la interfaz.

## 12.1 Instrumentos generales

Aplicables a todas o casi todas las categorías:

- EVA, cuando exista seguimiento de dolor.
- PGIC, como impresión global de cambio.

PGIC ya forma parte del registro por sesión, pero su periodicidad futura podrá
configurarse.

## 12.2 Instrumentos específicos previstos

| Categoría / subcategoría | PROM candidato |
|---|---|
| Rodilla | KOOS o WOMAC |
| Artrosis de rodilla | WOMAC y/o KOOS, según protocolo |
| Cadera | WOMAC |
| Columna lumbar / lumbalgia | ODI |
| Columna cervical / cervicalgia | NDI |
| Hombro | SPADI |
| Dolor general o persistente | PGIC y EVA |
| Estrés percibido | PSS |
| Síntomas de ansiedad | GAD-7 |
| Insomnio | ISI |
| Síndrome de intestino irritable | IBS-SSS |
| Asma documentada | ACT |
| EPOC documentada | CAT |

La asociación definitiva debe validarse clínicamente y respetar licencias,
versiones e idiomas autorizados.

## 12.3 Tabla conceptual `prom_catalog`

| Campo | Propósito |
|---|---|
| id | Identificador |
| code | Código estable del instrumento |
| name | Nombre |
| version | Versión |
| language | Idioma |
| license_status | Estado de autorización |
| implementation_status | No implementado, piloto o activo |
| active | Disponibilidad |

## 12.4 Tabla conceptual `classification_prom_rules`

| Campo | Propósito |
|---|---|
| id | Identificador |
| category_id | Regla general opcional |
| subcategory_id | Regla específica opcional |
| prom_id | Instrumento asociado |
| requirement_level | Obligatorio, recomendado u opcional |
| schedule | Basal, por sesión, periódico o final |
| interval_sessions | Frecuencia por número de sesiones |
| active | Vigencia de la regla |
| rule_version | Versión |
| valid_from / valid_to | Período de validez |

Las reglas específicas de subcategoría tendrán prioridad sobre las reglas
generales de categoría.

## 12.5 Flujo de activación

1. El profesional selecciona categoría y subcategoría.
2. El sistema consulta reglas activas.
3. Se muestran PROMs generales y específicos.
4. El profesional confirma los instrumentos aplicables.
5. Se crea un plan de medición para el paciente.
6. Se programan evaluaciones basales y de seguimiento.
7. Un cambio de clasificación propone revisar el plan, pero no elimina
   resultados anteriores.

## 12.6 Estados de un PROM para el paciente

- Sugerido.
- Confirmado.
- Pendiente.
- Completado.
- Incompleto.
- Suspendido.
- No aplicable.

Guardar solamente `assigned_scale` como texto no será suficiente para esta
etapa; deberá conservarse como dato histórico mientras se migra al plan
estructurado.

---

## 13. Consideraciones para investigación

La CAPA 2 debe permitir agrupar pacientes sin perder trazabilidad.

### Datos mínimos necesarios

- Código y versión de categoría.
- Código y versión de subcategoría.
- Fecha de inicio y fin de vigencia.
- Fuente de la clasificación.
- Profesional que la confirmó.
- PROMs activos durante cada período.

### Reglas de calidad

- No reclasificar retrospectivamente sin dejar historial.
- No combinar categorías distintas bajo un mismo nombre analítico.
- Diferenciar datos migrados de datos confirmados.
- Usar códigos estables en exportaciones.
- Registrar valores “pendiente” y “no aplicable” de forma diferenciada.
- Mantener el diagnóstico libre como dato separado.

### Exportación

Las exportaciones futuras deberán incluir:

- `category_code`.
- `subcategory_code`.
- `classification_version`.
- `classification_status`.
- `valid_from`.
- `valid_to`.

Los datos identificatorios deberán excluirse o seudonimizarse según el uso y la
normativa aplicable.

---

## 14. Alertas y validaciones UX

### Validaciones bloqueantes

- Categoría sin subcategoría en pacientes nuevos.
- Subcategoría incompatible con la categoría.
- Diagnóstico específico seleccionado sin diagnóstico documentado cuando la
  regla lo exige.
- “Otra condición” sin detalle.

### Advertencias no bloqueantes

- Clasificación migrada pendiente de revisión.
- Subcategoría sin PROM específico implementado.
- Cambio de clasificación con un plan de PROMs activo.
- Selección de “Pendiente de clasificación”.

### Mensajes recomendados

> La clasificación organiza el seguimiento y no constituye un diagnóstico.

> Este PROM está sugerido por la clasificación, pero todavía no está
> implementado.

> La clasificación cambió. Revise los PROMs activos antes de guardar.

---

## 15. Permisos y auditoría futura

- Solo profesionales autorizados podrán confirmar o cambiar la clasificación.
- Personal administrativo podrá visualizarla, pero no modificarla.
- Cada cambio deberá registrar usuario, fecha, valor anterior y valor nuevo.
- Las sugerencias generadas por IA deberán identificarse como tales.
- Ninguna sugerencia de IA se guardará como confirmada sin acción profesional.

---

## 16. Alcance de implementación recomendado

### Primera entrega de CAPA 2

- Catálogo de categorías y subcategorías.
- Selección dependiente en Registro de Paciente.
- Conservación del diagnóstico libre.
- Migración no destructiva de motivos existentes.
- Categoría y subcategoría en el dashboard.
- Filtros básicos.
- Sugerencia informativa de PROMs.

### Segunda entrega

- Edición controlada.
- Historial de clasificación.
- Estado de confirmación.
- Reglas de PROMs almacenadas en base de datos.
- Plan de medición por paciente.

### Tercera entrega

- Auditoría.
- Versionado de catálogos.
- Exportación para investigación.
- Sugerencias asistidas por IA con confirmación humana.

---

## 17. Criterios de aceptación

La CAPA 2 estará correctamente diseñada cuando:

- Cada paciente pueda tener una categoría y subcategoría válidas.
- El diagnóstico médico libre se conserve sin modificaciones.
- Los datos previos puedan migrarse sin pérdida.
- Las clasificaciones migradas sean distinguibles de las confirmadas.
- El dashboard permita identificar y filtrar grupos clínicos.
- Los códigos internos sean estables y exportables.
- Las opciones inactivas no desaparezcan de registros históricos.
- La clasificación pueda activar reglas de PROMs sin código rígido.
- Un cambio de clasificación no elimine PROMs ni sesiones anteriores.
- La aplicación no infiera ni emita diagnósticos.

---

## 18. Decisión arquitectónica recomendada

La categoría y la subcategoría no deben implementarse como dos textos libres ni
como una simple ampliación permanente de `main_complaint`.

La opción recomendada es:

1. Catálogos normalizados de categorías y subcategorías.
2. Una clasificación vigente vinculada al paciente.
3. Un historial de clasificaciones para trazabilidad.
4. Reglas configurables que vinculen clasificaciones con PROMs.
5. Conservación temporal de los campos actuales para compatibilidad.

Este enfoque permite evolucionar PROM-ACU por capas, protege los datos
existentes y prepara la aplicación para seguimiento clínico e investigación
sin convertir la clasificación en un sistema automático de diagnóstico.
