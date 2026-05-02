# Salones y clínicas — Plan de implementación local

> **Para Hermes:** este plan sirve como ruta de ejecución por módulos y por orden de entrega.

**Objetivo:** completar el MVP local del asistente para salones y clínicas con chat, reservas, notificaciones, dashboard y reglas de negocio.

**Arquitectura:** mantener el núcleo de dominio separado de la capa de orquestación (chat, dashboard y persistencia). Implementar primero la base local e in-memory/JSON para poder iterar rápido sin depender de servicios externos. Después conectar flujos de usuario, métricas del dueño y, al final, integraciones.

**Stack previsto:** Python 3.13, dataclasses, tests con unittest, persistencia local en JSON o SQLite, módulos bajo `src/salon_mvp/`.

---

## Estado actual

Ya existen:
- modelo de dominio (`domain.py`)
- flujo conversacional (`chat_flow.py`)
- dashboard del dueño (`dashboard.py`)
- tests de dominio, chat y dashboard

Queda por completar:
- persistencia
- servicio de agenda/booking
- reglas de disponibilidad
- panel administrativo y vistas operativas
- preparación para futuras integraciones

---

## Orden de ejecución recomendado

### 1) Persistencia local

**Objetivo:** guardar y cargar negocio, clientes, empleados, servicios, reservas y feedback sin depender de terceros.

**Archivos:**
- Crear: `src/salon_mvp/storage.py`
- Crear: `tests/test_storage.py`

**Tareas:**
- definir un repositorio local simple
- soportar guardar/cargar estado completo en JSON
- validar que el formato sea estable y legible

**Verificación:**
- guardar un estado de prueba
- cargarlo de nuevo
- comprobar que los objetos reconstruidos conservan ids y datos clave

---

### 2) Servicio de reservas

**Objetivo:** centralizar la creación, confirmación, cancelación y reprogramación de citas.

**Archivos:**
- Crear: `src/salon_mvp/booking_service.py`
- Crear: `tests/test_booking_service.py`

**Tareas:**
- crear reserva desde el flujo de chat
- aplicar recargos por empleado
- rechazar empleados inactivos o incompatibles
- marcar estados de cita correctamente

**Verificación:**
- crear una reserva válida
- confirmar una reserva
- cancelar una reserva
- comprobar precio final y estado

---

### 3) Reglas de disponibilidad y agenda

**Objetivo:** evitar choques de horario y permitir encontrar huecos disponibles.

**Archivos:**
- Crear: `src/salon_mvp/scheduling.py`
- Crear: `tests/test_scheduling.py`

**Tareas:**
- calcular slots disponibles por servicio y sede
- bloquear solapamientos por empleado
- sugerir el siguiente hueco útil

**Verificación:**
- dos reservas solapadas deben fallar
- una reserva en hueco libre debe pasar
- el sistema debe sugerir alternativas

---

### 4) Orquestación del chat

**Objetivo:** convertir el flujo conversacional en una experiencia operativa real.

**Archivos:**
- Crear: `src/salon_mvp/chat_orchestrator.py`
- Crear: `tests/test_chat_orchestrator.py`

**Tareas:**
- conectar `BookingChatFlow` con el servicio de reservas
- generar confirmaciones finales
- disparar la notificación al empleado
- guardar la conversación resumida

**Verificación:**
- una conversación completa termina en reserva
- la notificación contiene los datos correctos
- el resumen queda persistido

---

### 5) Dashboard operativo del dueño

**Objetivo:** ofrecer una vista útil para gerencia con métricas accionables.

**Archivos:**
- Crear: `src/salon_mvp/admin_views.py`
- Crear: `tests/test_admin_views.py`

**Tareas:**
- mostrar top clientes, empleados y servicios
- mostrar facturación, horas dedicadas y reputación
- añadir filtros por fecha y sede

**Verificación:**
- dashboard devuelve métricas coherentes
- los rankings cambian al cambiar los datos
- los filtros afectan al resultado esperado

---

### 6) Reglas de negocio avanzadas

**Objetivo:** formalizar lógica comercial: skills tipo FIFA, recargos, upselling, valoraciones y reputación.

**Archivos:**
- Modificar: `src/salon_mvp/domain.py`
- Modificar: `src/salon_mvp/dashboard.py`
- Crear: `tests/test_business_rules.py`

**Tareas:**
- refinar recargos por empleado
- añadir reglas de upsell/cross-sell configurables
- calcular reputación por dimensiones
- preparar incentivos o ranking interno de empleados

**Verificación:**
- el cálculo del precio final es estable
- la reputación se calcula por dimensión
- los rankings reflejan los datos reales

---

### 7) Preparación para integraciones externas

**Objetivo:** dejar puntos de extensión para Odoo, WhatsApp, correo o CRM.

**Archivos:**
- Crear: `src/salon_mvp/integrations/`
- Crear: `tests/test_integrations_contracts.py`

**Tareas:**
- definir interfaces de integración
- dejar adaptadores vacíos o simulados
- aislar dependencias externas

**Verificación:**
- el núcleo funciona sin integraciones
- los adaptadores no rompen el flujo local

---

## Criterio de cierre por fase

Una fase se considera terminada cuando:
- hay código funcional en `src/salon_mvp/`
- hay tests que cubren el comportamiento nuevo
- `python3 -m unittest discover -s tests -v` pasa completo
- el README refleja el nuevo estado

---

## Próximo paso inmediato

La siguiente pieza lógica es **persistencia local** porque desbloquea el resto del sistema sin meter complejidad innecesaria.
