# DOCUMENTO MAESTRO V2

## 1. Nombre de la aplicación

**PROM-ACU**

**Descripción breve:** plataforma de telemedicina asistida por inteligencia
artificial para el seguimiento clínico de pacientes tratados con acupuntura,
basada en resultados reportados por el paciente (PROMs), Escala Visual
Analógica del dolor (EVA), escalas funcionales validadas, gráficos de evolución
e informes automáticos.

**Advertencia clínica obligatoria:**

> Esta aplicación no reemplaza la consulta médica ni emite diagnósticos. Solo
> permite seguimiento clínico. Las decisiones diagnósticas y terapéuticas
> corresponden exclusivamente a profesionales habilitados.

---

## 2. Objetivo

PROM-ACU tiene como objetivo facilitar un seguimiento clínico estructurado,
longitudinal y comprensible de pacientes que reciben acupuntura.

La aplicación debe permitir:

- Registrar datos clínicos relevantes sin inventar diagnósticos.
- Medir síntomas y funcionalidad antes, durante y después del tratamiento.
- Recopilar PROMs en momentos definidos del seguimiento.
- Visualizar la evolución individual mediante indicadores y gráficos.
- Detectar cambios clínicos, falta de respuesta y posibles señales de alerta.
- Mejorar la comunicación entre paciente y profesional.
- Generar informes descriptivos que apoyen la documentación clínica.
- Reducir tareas administrativas repetitivas.

La plataforma no debe recomendar tratamientos, modificar medicación ni
interpretar los resultados como un diagnóstico automático.

---

## 3. Pacientes objetivo

La aplicación está dirigida a pacientes adultos en seguimiento profesional por
acupuntura, principalmente por:

- Dolor de rodilla.
- Dolor de cadera.
- Lumbalgia.
- Cervicalgia.
- Dolor de hombro.
- Dolor general o persistente.
- Estrés o ansiedad.
- Insomnio.
- Síntomas digestivos funcionales.
- Síntomas respiratorios funcionales.

En futuras versiones podrán contemplarse otros grupos, siempre con validación
clínica y adaptación de los instrumentos.

### Exclusiones iniciales

El MVP no está diseñado específicamente para:

- Emergencias médicas.
- Pacientes pediátricos.
- Seguimiento obstétrico.
- Personas sin evaluación profesional cuando esta sea necesaria.
- Uso autónomo para diagnóstico o automedicación.

Cuando exista una situación urgente o una señal de alarma, la aplicación debe
indicar que el paciente busque atención médica inmediata por los canales
locales correspondientes.

---

## 4. Flujo de atención

### 4.1 Alta del paciente

1. El profesional registra al paciente.
2. Se documentan sus datos identificatorios y de contacto.
3. Se registra el diagnóstico médico previamente establecido.
4. Se selecciona el motivo principal del seguimiento.
5. El sistema asigna las escalas sugeridas según ese motivo.
6. Se informa al paciente el alcance de la plataforma.
7. Se registra la aceptación de los términos y el consentimiento aplicable.

### 4.2 Evaluación basal

1. El paciente completa EVA y los PROMs asignados.
2. El profesional revisa la información.
3. Se establece la línea basal para comparaciones futuras.
4. Se registran medicación analgésica, limitaciones funcionales y observaciones.
5. Si aparece una alerta, el profesional debe revisarla antes de continuar.

### 4.3 Seguimiento por sesión

1. Se confirma la identidad del paciente.
2. Se registra EVA antes de la sesión.
3. Se documenta el número y la fecha de la sesión.
4. Se registra EVA después de la sesión.
5. Se documentan analgesia, eventos adversos y observaciones clínicas.
6. El sistema actualiza los indicadores y gráficos.

### 4.4 Evaluaciones periódicas

1. El sistema solicita nuevamente los PROMs en intervalos predefinidos.
2. Se comparan los resultados con la línea basal.
3. El profesional revisa evolución, adherencia y eventos adversos.
4. Se genera un informe de seguimiento.

### 4.5 Cierre o continuidad

1. Se realiza una medición final.
2. Se compara el estado final con el basal.
3. Se genera un informe clínico descriptivo.
4. El profesional documenta continuidad, alta o derivación fuera de la
   plataforma.

PROM-ACU no debe decidir automáticamente el alta ni la continuidad del
tratamiento.

---

## 5. Interacciones con el paciente

El paciente podrá interactuar mediante una interfaz simple, accesible desde
computadora o teléfono.

### Interacciones previstas

- Completar EVA y PROMs asignados.
- Consultar próximas evaluaciones pendientes.
- Registrar cambios relevantes desde la última sesión.
- Informar uso de medicación analgésica.
- Informar eventos adversos.
- Agregar comentarios breves sobre síntomas y funcionalidad.
- Ver una representación sencilla de su evolución.
- Recibir recordatorios de cuestionarios o sesiones.
- Consultar avisos de seguridad y canales de contacto.

### Principios de experiencia

- Lenguaje claro y no alarmista.
- Una pregunta por pantalla cuando sea conveniente.
- Escalas explicadas sin alterar su redacción validada.
- Confirmación antes de enviar datos.
- Accesibilidad visual y compatibilidad móvil.
- Posibilidad de solicitar ayuda al profesional.
- No mostrar conclusiones diagnósticas automáticas.
- No mostrar recomendaciones terapéuticas generadas por IA.

---

## 6. Funciones principales

### Gestión de pacientes

- Alta y edición de pacientes.
- Identificación mediante un registro único.
- Datos de contacto y datos clínicos mínimos.
- Motivo principal y diagnóstico médico registrado.
- Consentimientos y estado del seguimiento.

### Gestión clínica

- Asignación automática de escalas.
- Registro de evaluación basal.
- Registro de sesiones de acupuntura.
- EVA pre y pos sesión.
- Registro de analgesia.
- Registro de eventos adversos.
- Observaciones clínicas.
- Historial cronológico.

### Seguimiento de resultados

- Cálculo de mejoría absoluta.
- Cálculo de mejoría porcentual.
- Comparación con la línea basal.
- Evolución por sesión.
- Evolución de PROMs.
- Clasificación descriptiva de respuesta.
- Detección de datos faltantes y alertas.

### Comunicación y documentación

- Recordatorios.
- Informes automáticos.
- Exportación de informes.
- Resumen para el profesional.
- Vista simplificada para el paciente.
- Registro de auditoría en versiones posteriores.

---

## 7. PROMs incluidos

La elección de cada instrumento debe respetar su versión validada, licencia,
idioma, instrucciones, puntuación y población de uso.

| Motivo principal | Instrumentos previstos | Estado inicial |
|---|---|---|
| Rodilla | KOOS o WOMAC + EVA | EVA implementada; resto pendiente |
| Cadera | WOMAC + EVA | EVA implementada; WOMAC pendiente |
| Lumbalgia | ODI + EVA | EVA implementada; ODI pendiente |
| Cervicalgia | NDI + EVA | EVA implementada; NDI pendiente |
| Hombro | SPADI + EVA | EVA implementada; SPADI pendiente |
| Dolor general | EVA + PGIC | EVA implementada; PGIC pendiente |
| Estrés o ansiedad | GAD-7 + PSS | Pendiente |
| Insomnio | ISI | Pendiente |
| Digestivo funcional | IBS-SSS | Pendiente |
| Respiratorio funcional | ACT o CAT | Pendiente |

### EVA

- Rango: 0 a 10.
- Cero representa ausencia de dolor.
- Diez representa el peor dolor imaginable.
- Se registra, como mínimo, antes de cada sesión.
- Puede registrarse después de cada sesión para documentar el cambio inmediato.
- La EVA basal será la primera EVA pre sesión válida o una medición basal
  específica si se incorpora posteriormente.

### Requisitos para implementar otros PROMs

- Confirmar autorización de uso y licencias.
- Utilizar una traducción validada.
- Mantener intactas las preguntas y opciones de respuesta.
- Implementar el algoritmo oficial de puntuación.
- Documentar el manejo de respuestas incompletas.
- Mostrar fecha, versión y contexto de administración.
- No interpretar una puntuación aislada como diagnóstico.

---

## 8. Reglas clínicas básicas

Las reglas tienen fines descriptivos y de priorización. No reemplazan la
evaluación profesional.

### 8.1 Línea basal

- La EVA basal es la primera EVA pre sesión válida.
- No debe reemplazarse automáticamente por una medición posterior.
- Toda corrección debe quedar registrada en auditoría.

### 8.2 EVA actual

- La EVA actual corresponde a la EVA pre sesión más reciente.
- La EVA pos sesión se utiliza para evaluar cambio inmediato, no para sustituir
  la medición longitudinal pre sesión.

### 8.3 Mejoría absoluta

**Mejoría absoluta = EVA basal - EVA actual**

- Resultado positivo: reducción del dolor.
- Resultado cero: sin cambio.
- Resultado negativo: aumento del dolor.

### 8.4 Mejoría porcentual

**Mejoría porcentual = ((EVA basal - EVA actual) / EVA basal) × 100**

Consideraciones:

- Si la EVA basal es cero, no se debe aplicar la fórmula habitual.
- Si basal y actual son cero, se informará “sin cambio, EVA 0”.
- Si la basal es cero y la actual aumenta, se clasificará como empeoramiento.
- Los valores deben redondearse de forma consistente.

### 8.5 Clasificación descriptiva

| Resultado | Clasificación |
|---|---|
| Mejoría igual o superior al 70 % | Excelente respuesta |
| Mejoría entre 50 % y 69,9 % | Muy buena respuesta |
| Mejoría entre 30 % y 49,9 % | Moderada |
| Mejoría entre 10 % y 29,9 % | Leve |
| Mejoría inferior al 10 % | Sin respuesta clara |
| EVA actual mayor que EVA basal | Empeoramiento |

Esta clasificación es una regla interna del producto y no debe presentarse como
una conclusión diagnóstica ni como criterio universal de eficacia.

### 8.6 Integridad de datos

- No admitir EVA fuera del rango 0 a 10.
- No duplicar el número de sesión de un mismo paciente.
- No permitir fechas futuras salvo justificación explícita.
- Registrar la fecha y hora de creación y modificación.
- Diferenciar “No” de “Sin dato”.
- Identificar cuestionarios incompletos.
- No inventar valores faltantes.

---

## 9. Alertas

Las alertas deben ser visibles, trazables y revisables. Su propósito es señalar
información que requiere atención, no emitir un diagnóstico.

### Alertas clínicas de seguimiento

- EVA actual superior a la EVA basal.
- Aumento marcado de EVA entre sesiones consecutivas.
- Falta de mejoría después de un número configurable de sesiones.
- Evento adverso informado.
- Evento adverso descrito como intenso, persistente o inesperado.
- Incremento del uso de analgésicos.
- Empeoramiento relevante de un PROM.
- Cuestionarios repetidamente incompletos.
- Paciente sin seguimiento dentro del intervalo esperado.

### Señales de alarma declaradas por el paciente

El formulario previo debe incluir preguntas de seguridad definidas y validadas
por responsables clínicos. Ante una posible urgencia, la aplicación debe:

1. Mostrar un mensaje claro para buscar atención médica inmediata.
2. Indicar los canales de emergencia locales configurados.
3. Evitar continuar con cuestionarios no prioritarios.
4. Notificar al profesional según el protocolo institucional.
5. Registrar la alerta y las acciones realizadas.

La aplicación no debe intentar clasificar por IA una emergencia médica sin
protocolos clínicos, validación y supervisión adecuados.

### Niveles operativos sugeridos

- **Informativa:** dato pendiente o recordatorio.
- **Atención:** cambio que requiere revisión profesional.
- **Prioritaria:** evento adverso o deterioro significativo.
- **Urgente:** posible señal de alarma que requiere atención inmediata.

---

## 10. Dashboard médico

El dashboard debe ofrecer una visión rápida sin ocultar el detalle clínico.

### Vista general

- Número total de pacientes.
- Pacientes activos.
- Sesiones registradas.
- Evaluaciones pendientes.
- Alertas abiertas.
- Eventos adversos recientes.
- Pacientes sin seguimiento.

### Tabla de pacientes

- Nombre o identificador.
- Motivo principal.
- Diagnóstico médico registrado.
- Escalas asignadas.
- EVA basal.
- Última EVA.
- Mejoría absoluta.
- Mejoría porcentual.
- Número de sesiones.
- Última fecha de seguimiento.
- Estado clínico descriptivo.
- Indicador de alertas.

### Vista individual

- Datos principales del paciente.
- Línea temporal de sesiones.
- Gráfico de EVA pre sesión.
- Comparación EVA pre y pos sesión.
- Evolución de cada PROM.
- Uso de analgésicos.
- Eventos adversos.
- Observaciones clínicas.
- Evaluaciones pendientes.
- Informes disponibles.

### Filtros

- Estado del seguimiento.
- Motivo principal.
- Profesional.
- Período.
- Estado clínico.
- Presencia de alertas.
- Uso de analgésicos.
- Eventos adversos.

---

## 11. Informes automáticos

Los informes serán descriptivos, verificables y editables por el profesional.

### Contenido mínimo

- Identificación del paciente.
- Diagnóstico médico registrado.
- Motivo principal.
- Período del seguimiento.
- Número de sesiones.
- Escalas utilizadas.
- EVA basal.
- Última EVA pre sesión.
- Mejoría absoluta y porcentual.
- Clasificación descriptiva.
- Evolución de PROMs.
- Uso de medicación analgésica informado.
- Eventos adversos.
- Observaciones clínicas.
- Gráfico de evolución.
- Fecha de generación.
- Profesional responsable.
- Advertencia sobre el alcance del informe.

### Texto base

> Paciente [nombre], con diagnóstico médico registrado [diagnóstico], en
> seguimiento con acupuntura. EVA basal: [valor]. Última EVA registrada:
> [valor]. Mejoría absoluta: [valor]. Mejoría porcentual: [valor] %. Respuesta
> clínica descriptiva: [clasificación]. Eventos adversos informados: [sí/no].
> Observaciones: [texto].

### Formatos

- TXT para el MVP.
- PDF en una versión posterior.
- Exportación estructurada para interoperabilidad futura.

### Reglas de seguridad

- No generar diagnósticos nuevos.
- No recomendar cambios de tratamiento o medicación.
- Señalar datos faltantes.
- Diferenciar hechos registrados de resúmenes generados.
- Permitir revisión y aprobación profesional antes de compartir.
- Registrar quién generó, revisó y descargó el informe.

---

## 12. Base de datos

### Entidades principales

#### Pacientes

- Identificador interno.
- Nombre y apellido.
- Documento de identidad.
- Edad o fecha de nacimiento.
- Sexo registrado.
- Teléfono.
- Diagnóstico médico principal.
- Motivo principal.
- Escalas asignadas.
- Fecha de alta.
- Estado del seguimiento.

#### Sesiones

- Identificador.
- Paciente.
- Número de sesión.
- Fecha.
- EVA pre sesión.
- EVA pos sesión.
- Uso de analgésicos.
- Evento adverso.
- Descripción del evento adverso.
- Observaciones clínicas.
- Fecha de creación y modificación.

#### Evaluaciones PROM

- Identificador.
- Paciente.
- Instrumento.
- Versión e idioma.
- Fecha de administración.
- Respuestas.
- Puntuación total y subescalas.
- Estado: pendiente, completa o incompleta.
- Profesional revisor.

#### Alertas

- Identificador.
- Paciente.
- Tipo y nivel.
- Motivo.
- Fecha de generación.
- Estado: abierta, revisada o cerrada.
- Profesional responsable.
- Acción documentada.

#### Informes

- Identificador.
- Paciente.
- Período.
- Contenido o referencia al archivo.
- Fecha de generación.
- Autor.
- Estado de revisión.

#### Usuarios y auditoría

- Usuarios profesionales y administrativos.
- Roles y permisos.
- Accesos.
- Altas, modificaciones y eliminaciones lógicas.
- Exportaciones y descargas.
- Revisión y cierre de alertas.

### Requisitos de protección

- Cifrado en tránsito y en reposo.
- Control de acceso por roles.
- Autenticación segura.
- Sesiones con vencimiento.
- Copias de seguridad.
- Auditoría de acciones.
- Política de retención y eliminación.
- Separación entre ambientes de prueba y producción.
- Minimización de datos personales.
- Consentimiento y cumplimiento normativo aplicable.

SQLite es aceptable para una demo local. Una versión multiusuario debe utilizar
una base de datos administrada, con backups, controles de concurrencia y
monitoreo.

---

## 13. Futuras funciones con IA

Toda función de IA debe ser asistiva, explicable, supervisada y evaluada antes
de utilizarse con datos reales.

### Funciones propuestas

- Resumen automático de la evolución longitudinal.
- Borrador de informe clínico para revisión profesional.
- Identificación de datos faltantes o inconsistentes.
- Priorización de pacientes con alertas.
- Agrupación de observaciones clínicas por tema.
- Conversión de notas libres en campos estructurados, con confirmación.
- Explicación de gráficos en lenguaje claro.
- Recordatorios personalizados según adherencia.
- Detección de patrones de respuesta para investigación.
- Asistente para seleccionar el PROM correspondiente según reglas aprobadas.
- Transcripción y resumen de consultas con consentimiento.

### Límites obligatorios

La IA no debe:

- Diagnosticar.
- Prescribir.
- Indicar puntos o técnicas de acupuntura.
- Cambiar tratamientos o medicación.
- Ocultar incertidumbre.
- Completar datos clínicos inexistentes.
- Cerrar alertas sin intervención humana.
- Comunicarse con el paciente en nombre del profesional sin controles.

### Gobernanza

- Aprobación humana antes de utilizar o compartir contenido generado.
- Registro de versión del modelo y del texto generado.
- Evaluación periódica de calidad, sesgos y errores.
- Protección de datos y contratos adecuados con proveedores.
- Posibilidad de desactivar las funciones de IA.
- Separación visual entre datos originales y contenido generado.

---

## 14. Paso a paso para construir la aplicación

### Etapa 1: definición clínica y legal

1. Definir responsables clínicos y técnicos.
2. Confirmar población, alcance y exclusiones.
3. Validar reglas de seguimiento y alertas.
4. Revisar licencias y versiones de cada PROM.
5. Definir consentimiento, privacidad y retención de datos.
6. Establecer protocolos para eventos adversos y urgencias.

### Etapa 2: diseño funcional

1. Documentar casos de uso.
2. Diseñar el flujo del profesional y del paciente.
3. Definir campos obligatorios y opcionales.
4. Diseñar estados de pacientes, cuestionarios y alertas.
5. Crear prototipos de las pantallas.
6. Validar lenguaje y accesibilidad con usuarios.

### Etapa 3: arquitectura y seguridad

1. Seleccionar arquitectura de desarrollo y producción.
2. Diseñar el modelo de datos.
3. Definir autenticación y permisos.
4. Diseñar auditoría y backups.
5. Definir cifrado y gestión de secretos.
6. Separar ambientes y datos de prueba.

### Etapa 4: MVP clínico

1. Crear registro de pacientes.
2. Implementar asignación de escalas.
3. Implementar EVA basal, pre y pos sesión.
4. Crear registro de sesiones.
5. Implementar cálculos de evolución.
6. Crear dashboard individual y general.
7. Generar informe TXT.
8. Incorporar advertencias y validaciones.

### Etapa 5: PROMs validados

1. Implementar cada instrumento con su versión autorizada.
2. Agregar algoritmos oficiales de puntuación.
3. Validar resultados con casos de referencia.
4. Incorporar periodicidad y recordatorios.
5. Mostrar evolución por escala y subescala.

### Etapa 6: portal del paciente

1. Crear acceso seguro.
2. Implementar cuestionarios móviles.
3. Incorporar consentimiento y confirmación de identidad.
4. Agregar recordatorios y notificaciones.
5. Crear una vista comprensible de evolución.
6. Implementar canales seguros de contacto.

### Etapa 7: alertas y operación

1. Implementar reglas configurables.
2. Crear bandeja de alertas.
3. Definir responsables y tiempos de respuesta.
4. Registrar revisión y resolución.
5. Probar los protocolos con escenarios simulados.

### Etapa 8: informes y exportaciones

1. Implementar informes PDF.
2. Agregar revisión y firma profesional.
3. Incorporar gráficos y resultados PROM.
4. Implementar exportaciones con permisos.
5. Preparar interoperabilidad futura.

### Etapa 9: IA asistiva

1. Seleccionar funciones de bajo riesgo.
2. Preparar datos anonimizados para evaluación.
3. Diseñar revisión humana obligatoria.
4. Medir precisión, omisiones y alucinaciones.
5. Implementar trazabilidad y controles.
6. Realizar un piloto limitado antes del uso general.

### Etapa 10: validación y despliegue

1. Realizar pruebas funcionales, clínicas y de seguridad.
2. Probar accesibilidad y experiencia móvil.
3. Ejecutar pruebas de recuperación y backups.
4. Capacitar a profesionales.
5. Desplegar inicialmente con pocos usuarios.
6. Monitorear incidentes, alertas y calidad de datos.
7. Revisar periódicamente las reglas y el producto.

---

## 15. Roadmap de versiones

### Versión 0.1: prototipo local

- Registro de pacientes.
- Asignación automática de escalas.
- Registro de sesiones.
- EVA pre y pos sesión.
- Cálculo de evolución.
- Dashboard básico.
- Gráfico de EVA.
- Informe TXT.
- SQLite local.

### Versión 0.2: calidad del MVP

- Edición controlada de pacientes y sesiones.
- Búsqueda y filtros.
- Mejor manejo de errores.
- Validación de fechas y datos faltantes.
- Exportación de datos.
- Informes mejorados.
- Pruebas automatizadas.

### Versión 0.3: PROMs funcionales

- Implementación progresiva de ODI, NDI, SPADI, WOMAC y PGIC.
- Puntuación validada.
- Calendario de evaluaciones.
- Gráficos por PROM.
- Gestión de cuestionarios incompletos.

### Versión 0.4: seguridad y multiusuario

- Base de datos administrada.
- Autenticación.
- Roles y permisos.
- Auditoría.
- Cifrado y backups.
- Separación de organizaciones o centros.

### Versión 0.5: portal del paciente

- Acceso móvil seguro.
- PROMs remotos.
- Recordatorios.
- Registro de eventos adversos.
- Vista simplificada de evolución.
- Consentimientos.

### Versión 0.6: alertas clínicas

- Reglas configurables.
- Bandeja de alertas.
- Priorización y responsables.
- Protocolos de revisión.
- Seguimiento de tiempos de respuesta.

### Versión 0.7: informes profesionales

- Informes PDF.
- Plantillas configurables.
- Revisión y aprobación.
- Firma o identificación profesional.
- Comparativas por períodos.

### Versión 0.8: IA asistiva controlada

- Resumen longitudinal.
- Borrador de informes.
- Detección de inconsistencias.
- Priorización asistida de alertas.
- Trazabilidad y revisión humana obligatoria.

### Versión 1.0: producto validado

- Validación clínica y de usabilidad.
- Seguridad evaluada.
- Operación multiusuario estable.
- PROMs autorizados y documentados.
- Portal profesional y del paciente.
- Alertas e informes auditables.
- Monitoreo, soporte y gestión de incidentes.

### Versiones posteriores

- Interoperabilidad con historias clínicas.
- Integración mediante estándares como FHIR cuando corresponda.
- Analítica poblacional anonimizada.
- Estudios observacionales y soporte para investigación.
- Aplicaciones móviles nativas si existe necesidad validada.
- Nuevos PROMs y especialidades con revisión clínica.

---

## Criterios generales de aceptación

PROM-ACU debe considerarse apta para avanzar de versión únicamente cuando:

- Las funciones previstas hayan sido probadas.
- Los cálculos coincidan con casos de referencia.
- Las escalas respeten sus versiones validadas y licencias.
- Las advertencias sean visibles.
- Los datos faltantes no se oculten ni se inventen.
- Las alertas tengan un responsable y un protocolo.
- Los informes sean revisables por un profesional.
- La privacidad y seguridad sean adecuadas al entorno de uso.
- La IA permanezca bajo supervisión humana.

Este documento define la visión funcional de PROM-ACU V2 y debe revisarse
conjuntamente por responsables clínicos, legales, de seguridad, diseño y
desarrollo antes de utilizar la aplicación con pacientes reales.
