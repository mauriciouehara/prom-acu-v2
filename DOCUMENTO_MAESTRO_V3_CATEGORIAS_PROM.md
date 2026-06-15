# DOCUMENTO MAESTRO V3: CATEGORÍAS Y PROMs

## 1. Propósito del documento

Este documento define la arquitectura clínica definitiva de PROM-ACU para la
**CAPA 2: Clasificación clínica del paciente**.

PROM-ACU es una plataforma clínica y de investigación basada en resultados
reportados por los pacientes (PROMs), orientada al seguimiento de personas
tratadas con acupuntura y medicina integrativa.

La arquitectura establece:

- Una categoría clínica principal.
- Una subcategoría clínica.
- Un PROM sugerido según la subcategoría.
- Un núcleo universal de seguimiento.
- El alcance exacto de implementación de la CAPA 2.
- La preparación necesaria para activar PROMs específicos en versiones futuras.

> PROM-ACU no emite diagnósticos ni reemplaza la evaluación profesional. La
> clasificación clínica debe ser seleccionada o confirmada por un profesional
> habilitado.

---

## 2. Principios clínicos y arquitectónicos

### 2.1 Clasificación estructurada

Cada paciente tendrá:

1. Una categoría clínica principal.
2. Una subcategoría perteneciente a esa categoría.
3. Un PROM sugerido por la arquitectura clínica.

### 2.2 Separación entre clasificación y diagnóstico

La categoría y la subcategoría organizan el seguimiento, pero no sustituyen el
diagnóstico médico registrado como texto clínico.

La aplicación no debe deducir automáticamente un diagnóstico desde síntomas,
PROMs, EVA, PGIC o notas clínicas.

### 2.3 PROM sugerido, no administrado

En la CAPA 2, el sistema mostrará qué PROM corresponde a la subcategoría, pero
no implementará todavía los cuestionarios específicos.

El estado visible será:

> PROM sugerido: [instrumento]. Pendiente de implementación.

### 2.4 Núcleo universal

Todos los pacientes compartirán un conjunto mínimo de variables de seguimiento.
Los instrumentos específicos se añadirán sobre ese núcleo en versiones
posteriores.

### 2.5 Datos aptos para investigación

Las categorías, subcategorías y PROMs deben utilizar códigos internos estables.
Los textos visibles podrán evolucionar sin alterar la interpretación de los
datos históricos.

---

## 3. Arquitectura clínica definitiva

# CATEGORÍA 1: Musculoesquelético

## Objetivo

Clasificar cuadros localizados o generalizados del sistema
musculoesquelético que son objeto de seguimiento clínico.

## Subcategorías y PROMs

| Subcategoría | PROM recomendado | Núcleo complementario |
|---|---|---|
| Rodilla | WOMAC / KOOS | EVA si hay dolor, PGIC e impacto funcional global |
| Cadera | WOMAC | EVA si hay dolor, PGIC e impacto funcional global |
| Lumbar | ODI | EVA si hay dolor, PGIC e impacto funcional global |
| Cervical | NDI | EVA si hay dolor, PGIC e impacto funcional global |
| Hombro | SPADI | EVA si hay dolor, PGIC e impacto funcional global |
| Dolor musculoesquelético generalizado | EVA + PGIC + impacto funcional global | Medicación relevante y eventos adversos |

## Códigos internos sugeridos

| Código de categoría | Código de subcategoría |
|---|---|
| MSK | MSK_KNEE |
| MSK | MSK_HIP |
| MSK | MSK_LUMBAR |
| MSK | MSK_CERVICAL |
| MSK | MSK_SHOULDER |
| MSK | MSK_GENERALIZED |

## Consideraciones

- WOMAC y KOOS no deben considerarse automáticamente equivalentes.
- La selección definitiva entre WOMAC y KOOS requerirá un protocolo clínico.
- La subcategoría describe el área principal de seguimiento y no confirma una
  etiología específica.

---

# CATEGORÍA 2: Reumatología

## Objetivo

Clasificar pacientes con una enfermedad reumatológica previamente documentada
que requiera seguimiento mediante PROMs.

## Subcategorías y PROMs

| Subcategoría | PROM recomendado | Núcleo complementario |
|---|---|---|
| Artrosis generalizada | WOMAC + EVA + PGIC | Impacto funcional global |
| Artritis reumatoidea | HAQ | EVA si hay dolor, PGIC e impacto funcional global |
| Espondiloartritis | BASDAI | EVA si hay dolor, PGIC e impacto funcional global |
| Fibromialgia | FIQR | EVA si hay dolor, PGIC e impacto funcional global |
| Otra enfermedad reumatológica | EVA + PGIC + impacto funcional global | Medicación relevante y eventos adversos |

## Códigos internos sugeridos

| Código de categoría | Código de subcategoría |
|---|---|
| RHEUM | RHEUM_GENERALIZED_OA |
| RHEUM | RHEUM_RA |
| RHEUM | RHEUM_SPA |
| RHEUM | RHEUM_FIBROMYALGIA |
| RHEUM | RHEUM_OTHER |

## Consideraciones

- Estas subcategorías exigen un diagnóstico previamente documentado.
- PROM-ACU no debe clasificar automáticamente una enfermedad reumatológica.
- La actividad clínica no debe determinarse a partir de un único PROM sin
  evaluación profesional.

---

# CATEGORÍA 3: Salud mental y sueño

## Objetivo

Organizar el seguimiento de estrés, síntomas emocionales y alteraciones del
sueño mediante instrumentos reportados por el paciente.

## Subcategorías y PROMs

| Subcategoría | PROM recomendado | Núcleo complementario |
|---|---|---|
| Estrés | PSS-10 | PGIC, impacto funcional global y eventos adversos |
| Ansiedad | GAD-7 | PGIC, impacto funcional global y eventos adversos |
| Depresión | PHQ-9 | PGIC, impacto funcional global y eventos adversos |
| Insomnio | ISI | PGIC, impacto funcional global y medicación relevante |

## Códigos internos sugeridos

| Código de categoría | Código de subcategoría |
|---|---|
| MENTAL_SLEEP | MS_STRESS |
| MENTAL_SLEEP | MS_ANXIETY |
| MENTAL_SLEEP | MS_DEPRESSION |
| MENTAL_SLEEP | MS_INSOMNIA |

## Consideraciones

- Las puntuaciones no deben mostrarse como diagnósticos automáticos.
- PHQ-9 y otros instrumentos con respuestas sensibles requerirán protocolos de
  seguridad antes de su implementación.
- La futura incorporación de alertas deberá ser validada por responsables
  clínicos y no depender exclusivamente de IA.

---

# CATEGORÍA 4: Digestivo funcional

## Objetivo

Clasificar cuadros digestivos funcionales documentados para seguimiento de
síntomas e impacto percibido.

## Subcategorías y PROMs

| Subcategoría | PROM recomendado | Núcleo complementario |
|---|---|---|
| Colon irritable | IBS-SSS | PGIC, impacto funcional global y medicación relevante |
| Dispepsia funcional | PAGI-SYM | PGIC, impacto funcional global y medicación relevante |
| Reflujo | GERD-Q | PGIC, impacto funcional global y medicación relevante |
| Estreñimiento funcional | PAC-SYM | PGIC, impacto funcional global y medicación relevante |

## Códigos internos sugeridos

| Código de categoría | Código de subcategoría |
|---|---|
| GI | GI_IBS |
| GI | GI_FUNCTIONAL_DYSPEPSIA |
| GI | GI_REFLUX |
| GI | GI_FUNCTIONAL_CONSTIPATION |

## Consideraciones

- La clasificación no debe retrasar una consulta médica ante señales de alarma.
- La aplicación no debe asumir que un síntoma digestivo es funcional sin
  evaluación previa.
- Cada PROM deberá implementarse en una versión validada y autorizada.

---

# CATEGORÍA 5: Respiratorio funcional

## Objetivo

Organizar el seguimiento funcional de cuadros respiratorios documentados.

## Subcategorías y PROMs

| Subcategoría | PROM recomendado | Núcleo complementario |
|---|---|---|
| Asma | ACT | PGIC, impacto funcional global y medicación relevante |
| EPOC | CAT | PGIC, impacto funcional global y medicación relevante |
| Rinitis | SNOT-22 o mini-RQLQ | PGIC, impacto funcional global y medicación relevante |
| Disnea funcional | mMRC | PGIC, impacto funcional global y eventos adversos |

## Códigos internos sugeridos

| Código de categoría | Código de subcategoría |
|---|---|
| RESP | RESP_ASTHMA |
| RESP | RESP_COPD |
| RESP | RESP_RHINITIS |
| RESP | RESP_FUNCTIONAL_DYSPNEA |

## Consideraciones

- ACT corresponde al seguimiento de asma.
- CAT corresponde al seguimiento de EPOC.
- La elección entre SNOT-22 y mini-RQLQ requerirá definición protocolar.
- mMRC mide disnea y no debe utilizarse como diagnóstico.
- Los síntomas respiratorios urgentes deben derivarse a los canales de atención
  correspondientes.

---

# CATEGORÍA 6: Otros / Integrativo

## Objetivo

Clasificar cuadros de seguimiento integrativo que no pertenecen de forma
principal a las categorías anteriores.

## Subcategorías y PROMs

| Subcategoría | PROM recomendado | Núcleo complementario |
|---|---|---|
| Fatiga crónica | FSS | PGIC, impacto funcional global y medicación relevante |
| Post-COVID | EQ-5D + FSS | PGIC, impacto funcional global y eventos adversos |
| Cefalea / migraña | HIT-6 | EVA si hay dolor, PGIC e impacto funcional global |
| Neuropatía | EVA + impacto funcional global | PGIC, medicación relevante y eventos adversos |
| Otro | EVA + PGIC + impacto funcional global | Medicación relevante y eventos adversos |

## Códigos internos sugeridos

| Código de categoría | Código de subcategoría |
|---|---|
| INTEGRATIVE | INT_CHRONIC_FATIGUE |
| INTEGRATIVE | INT_POST_COVID |
| INTEGRATIVE | INT_HEADACHE_MIGRAINE |
| INTEGRATIVE | INT_NEUROPATHY |
| INTEGRATIVE | INT_OTHER |

## Consideraciones

- “Otro” exigirá una descripción clínica.
- Post-COVID deberá utilizarse únicamente cuando el antecedente esté
  documentado.
- Neuropatía no debe inferirse automáticamente desde la descripción del dolor.
- EQ-5D puede estar sujeto a condiciones de uso y licencia.

---

## 4. Matriz clínica consolidada

| Categoría | Subcategoría | PROM recomendado |
|---|---|---|
| Musculoesquelético | Rodilla | WOMAC / KOOS |
| Musculoesquelético | Cadera | WOMAC |
| Musculoesquelético | Lumbar | ODI |
| Musculoesquelético | Cervical | NDI |
| Musculoesquelético | Hombro | SPADI |
| Musculoesquelético | Dolor musculoesquelético generalizado | EVA + PGIC + impacto funcional global |
| Reumatología | Artrosis generalizada | WOMAC + EVA + PGIC |
| Reumatología | Artritis reumatoidea | HAQ |
| Reumatología | Espondiloartritis | BASDAI |
| Reumatología | Fibromialgia | FIQR |
| Reumatología | Otra enfermedad reumatológica | EVA + PGIC + impacto funcional global |
| Salud mental y sueño | Estrés | PSS-10 |
| Salud mental y sueño | Ansiedad | GAD-7 |
| Salud mental y sueño | Depresión | PHQ-9 |
| Salud mental y sueño | Insomnio | ISI |
| Digestivo funcional | Colon irritable | IBS-SSS |
| Digestivo funcional | Dispepsia funcional | PAGI-SYM |
| Digestivo funcional | Reflujo | GERD-Q |
| Digestivo funcional | Estreñimiento funcional | PAC-SYM |
| Respiratorio funcional | Asma | ACT |
| Respiratorio funcional | EPOC | CAT |
| Respiratorio funcional | Rinitis | SNOT-22 o mini-RQLQ |
| Respiratorio funcional | Disnea funcional | mMRC |
| Otros / Integrativo | Fatiga crónica | FSS |
| Otros / Integrativo | Post-COVID | EQ-5D + FSS |
| Otros / Integrativo | Cefalea / migraña | HIT-6 |
| Otros / Integrativo | Neuropatía | EVA + impacto funcional global |
| Otros / Integrativo | Otro | EVA + PGIC + impacto funcional global |

---

## 5. Núcleo universal de seguimiento

El núcleo universal es el conjunto mínimo de variables comunes que permitirá
comparar la evolución dentro de cada paciente, incluso antes de implementar los
PROMs específicos.

## 5.1 EVA si hay dolor

- Escala de 0 a 10.
- Se utilizará cuando el paciente presente dolor como variable relevante.
- Se conservará la lógica existente de EVA basal, EVA pre sesión y EVA pos
  sesión.
- La ausencia de dolor como variable de seguimiento debe diferenciarse de una
  EVA igual a cero.

## 5.2 PGIC

Pregunta:

> Comparado con el inicio del tratamiento, ¿cómo se encuentra hoy?

Opciones:

1. Mucho peor.
2. Peor.
3. Igual.
4. Levemente mejor.
5. Moderadamente mejor.
6. Mucho mejor.
7. Completamente mejor.

PGIC ya está incorporado en el registro de sesión y continuará formando parte
del núcleo universal.

## 5.3 Impacto funcional global

Pregunta propuesta:

> En una escala de 0 a 10, ¿cuánto afecta actualmente su problema principal a
> sus actividades habituales?

Interpretación operativa:

- 0: no afecta sus actividades habituales.
- 10: impide por completo sus actividades habituales.

Características:

- Valor entero o decimal entre 0 y 10, según la decisión de implementación.
- Debe registrarse con una redacción estable.
- No sustituye los PROMs funcionales específicos.
- Permitirá seguimiento transversal mientras los instrumentos específicos
  permanezcan pendientes.
- No debe utilizarse como una escala validada equivalente a ODI, NDI, SPADI,
  WOMAC u otros instrumentos.

## 5.4 Uso de medicación relevante

Debe registrarse si el paciente utilizó medicación relevante para el problema
seguido.

En futuras versiones podrá incluir:

- Tipo de medicación.
- Frecuencia.
- Cambio respecto del período anterior.

La plataforma no recomendará iniciar, suspender ni modificar medicación.

## 5.5 Eventos adversos

Debe conservarse:

- Presencia o ausencia.
- Descripción.
- Fecha.
- Relación temporal con la sesión.

La interpretación clínica y cualquier acción corresponden al profesional.

---

## 6. Alcance funcional de la CAPA 2

La CAPA 2 implementará únicamente cuatro componentes nuevos o ampliados.

## 6.1 Categoría clínica

El profesional seleccionará una de las seis categorías definitivas:

1. Musculoesquelético.
2. Reumatología.
3. Salud mental y sueño.
4. Digestivo funcional.
5. Respiratorio funcional.
6. Otros / Integrativo.

## 6.2 Subcategoría

La lista de subcategorías dependerá de la categoría seleccionada.

La aplicación deberá impedir combinaciones incompatibles, por ejemplo:

- Reumatología + Insomnio.
- Digestivo funcional + Hombro.
- Respiratorio funcional + Fibromialgia.

## 6.3 PROM sugerido

Al seleccionar una subcategoría, la aplicación mostrará el PROM recomendado
según la matriz clínica.

Ejemplo:

> Categoría: Musculoesquelético  
> Subcategoría: Lumbar  
> PROM sugerido: ODI  
> Estado: pendiente de implementación

En esta capa, la sugerencia será informativa. No se administrará el
cuestionario.

## 6.4 Impacto funcional global 0-10

Se incorporará al seguimiento mediante la pregunta y los anclajes definidos en
este documento.

Deberá mostrarse:

- En el registro correspondiente.
- En el dashboard.
- En la evolución individual.
- En el informe clínico.

Su evolución se comparará descriptivamente, sin convertirla en un PROM
validado.

---

## 7. Experiencia de usuario prevista

## 7.1 Registro de Paciente

El bloque clínico tendrá el siguiente orden:

1. Diagnóstico médico principal registrado.
2. Categoría clínica.
3. Subcategoría.
4. PROM sugerido.

El PROM sugerido será de solo lectura y se actualizará al cambiar la
subcategoría.

Mensaje permanente:

> La clasificación organiza el seguimiento. No constituye un diagnóstico
> automático.

## 7.2 Registro de seguimiento

El núcleo universal mostrará:

- EVA, si hay dolor.
- PGIC.
- Impacto funcional global 0-10.
- Uso de medicación relevante.
- Eventos adversos.

## 7.3 Dashboard

La tabla general incorporará:

- Categoría.
- Subcategoría.
- PROM sugerido.
- Último impacto funcional global.

La vista individual mostrará:

- Clasificación clínica.
- PROM sugerido.
- Evolución de EVA cuando corresponda.
- Evolución de PGIC.
- Evolución del impacto funcional global.

## 7.4 Informes

El informe incorporará:

- Categoría clínica.
- Subcategoría.
- PROM sugerido.
- Impacto funcional global basal y más reciente, cuando estén disponibles.

El informe deberá indicar que el PROM específico está pendiente si todavía no
se administra.

---

## 8. Almacenamiento conceptual

La arquitectura deberá separar:

- Catálogo de categorías.
- Catálogo de subcategorías.
- Catálogo de PROMs.
- Asociación entre subcategoría y PROM sugerido.
- Clasificación vigente del paciente.
- Mediciones universales por sesión o evaluación.

## 8.1 Identificadores estables

Cada entidad debe poseer:

- Un identificador interno.
- Un código clínico estable.
- Un nombre visible.
- Un estado activo o inactivo.

## 8.2 Compatibilidad

Los campos actuales de motivo principal, diagnóstico y escala asignada no deben
eliminarse durante la transición.

Los pacientes existentes deberán migrarse sin pérdida y quedar identificados
como pendientes de confirmación profesional cuando el mapeo no sea inequívoco.

## 8.3 Impacto funcional global

Cada medición deberá asociarse al paciente y al momento del seguimiento.

Deberá conservar:

- Valor 0-10.
- Fecha.
- Contexto de registro.
- Sesión asociada, cuando corresponda.

---

## 9. Qué NO se implementará todavía

La CAPA 2 no incluirá:

- WOMAC completo.
- KOOS completo.
- ODI.
- NDI.
- SPADI.
- HAQ.
- FIQR.
- BASDAI.
- PSS-10.
- GAD-7.
- PHQ-9.
- ISI.
- IBS-SSS.
- PAGI-SYM.
- GERD-Q.
- PAC-SYM.
- ACT.
- CAT.
- SNOT-22.
- mini-RQLQ.
- mMRC.
- FSS.
- EQ-5D.
- HIT-6.
- Formularios automáticos de puntuación.
- Interpretación automática de resultados.
- Reglas de alertas basadas en esos instrumentos.
- Inteligencia artificial.
- Portal del paciente.
- Aplicación móvil nativa.
- Base de datos online.
- Autenticación multiusuario.
- Integración con historias clínicas externas.

La mención de un PROM en la interfaz no significará que el cuestionario esté
implementado o validado dentro de PROM-ACU.

---

## 10. Activación futura de PROMs específicos

La CAPA 2 funcionará como capa de clasificación y enrutamiento.

## 10.1 Flujo futuro

1. El profesional selecciona categoría.
2. Selecciona subcategoría.
3. El sistema consulta la matriz de asociación.
4. Muestra el PROM sugerido.
5. Cuando el instrumento esté implementado, el profesional podrá activarlo.
6. Se generará una evaluación basal.
7. Se programarán nuevas evaluaciones según el protocolo.
8. Los resultados se mostrarán junto al núcleo universal.

## 10.2 Estados futuros del PROM

- Sugerido.
- Pendiente de implementación.
- Disponible.
- Activado para el paciente.
- Evaluación pendiente.
- Completado.
- Incompleto.
- Suspendido.
- No aplicable.

## 10.3 Reglas configurables

La asociación no debe quedar escrita de forma rígida dentro de las pantallas.
Debe existir una matriz configurable que vincule:

- Categoría.
- Subcategoría.
- PROM.
- Nivel de recomendación.
- Frecuencia.
- Estado de implementación.
- Versión del instrumento.
- Idioma.
- Licencia.

## 10.4 Prioridad de reglas

Las reglas de una subcategoría tendrán prioridad sobre las reglas generales.

Ejemplo:

- Núcleo universal: PGIC.
- Regla de Musculoesquelético con dolor: EVA.
- Regla de Lumbar: ODI.

Resultado futuro:

> EVA + PGIC + impacto funcional global + ODI

## 10.5 Conservación histórica

Un cambio de categoría o subcategoría:

- No eliminará mediciones previas.
- No reasignará retrospectivamente cuestionarios.
- No modificará puntuaciones anteriores.
- Deberá quedar registrado con fecha.

---

## 11. Requisitos de calidad clínica para futuros PROMs

Antes de activar cualquier instrumento deberá confirmarse:

- Versión exacta.
- Idioma y traducción validada.
- Permiso o licencia de uso.
- Población objetivo.
- Algoritmo de puntuación.
- Manejo de respuestas incompletas.
- Momentos de administración.
- Interpretación permitida.
- Alertas requeridas.
- Validación mediante casos de prueba.

Ningún PROM debe implementarse copiando preguntas desde una fuente no
verificada.

---

## 12. Utilidad clínica e investigativa

Esta arquitectura permitirá:

- Agrupar pacientes por categoría y subcategoría.
- Comparar evolución dentro de grupos homogéneos.
- Identificar qué PROM corresponde a cada población.
- Mantener un núcleo común para análisis transversales.
- Incorporar instrumentos gradualmente.
- Diferenciar instrumentos sugeridos de instrumentos administrados.
- Preservar datos longitudinales ante cambios de clasificación.

Los análisis poblacionales deberán considerar diagnóstico, tratamiento,
duración, medicación, pérdidas de seguimiento y otras variables de confusión.
Los resultados descriptivos no implicarán causalidad ni eficacia terapéutica.

---

## 13. Criterios de aceptación de CAPA 2

La CAPA 2 se considerará correctamente implementada cuando:

- Cada paciente tenga una categoría válida.
- Cada paciente tenga una subcategoría compatible.
- El PROM sugerido coincida con la matriz de este documento.
- El PROM aparezca como pendiente y no como cuestionario administrado.
- Se registre impacto funcional global entre 0 y 10.
- El dashboard muestre clasificación, PROM sugerido e impacto funcional.
- El informe incluya esos datos.
- Los registros anteriores se conserven.
- La lógica actual de EVA y PGIC no se deteriore.
- La aplicación no emita diagnósticos.

---

## 14. Decisión final de arquitectura

PROM-ACU adoptará una arquitectura clínica compuesta por:

1. **Seis categorías clínicas definitivas.**
2. **Subcategorías cerradas y dependientes de cada categoría.**
3. **Un PROM recomendado por subcategoría.**
4. **Un núcleo universal de seguimiento.**
5. **Una matriz configurable para activar PROMs futuros.**

La CAPA 2 implementará solamente:

- Categoría clínica.
- Subcategoría.
- PROM sugerido.
- Impacto funcional global 0-10.

Los PROMs específicos permanecerán pendientes hasta que cada instrumento haya
sido revisado, autorizado, implementado y validado.

Esta decisión permite avanzar de forma incremental sin rehacer PROM-ACU,
mantiene el foco clínico-investigativo y evita convertir una sugerencia de
seguimiento en una conclusión diagnóstica.
