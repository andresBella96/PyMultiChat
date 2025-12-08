![Banner PyMultiChat](docs/banner_pymultichat.png)

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Estado](https://img.shields.io/badge/estado-proyecto%20formativo-informational)
![Plataforma](https://img.shields.io/badge/plataforma-linux%20%7C%20windows%20%7C%20macos-lightgrey)

🌐 **Idiomas disponibles:** [English](README.md) • [Español](README_ES.md)

---

PyMultiChat es un sistema de chat distribuido escrito en Python que implementa **dos versiones independientes** del mismo concepto:

1. **Chat UDP** — rápido, sin conexión persistente (*connectionless*)  
2. **Chat TCP multihilo** — comunicación continua por socket para cada cliente

Está pensado como proyecto didáctico para aprender **programación de redes, sockets, concurrencia y TUI (interfaz en terminal)** en Python.

---

## 🧠 Ideas de diseño clave

### 1. Protocolo ligero con alias

Tanto en TCP como en UDP se usa un formato común de mensaje:

```text
[Alias] mensaje
```

Encima de este formato se definen algunos mensajes internos especiales:

- `__HELLO__` → un usuario se conecta
- `__LEAVE__` → un usuario se desconecta
- `__USERS__` → el servidor envía la lista de usuarios ya conectados

Gracias a este mini‑protocolo:

- el cliente puede saber fácilmente quién ha enviado cada mensaje  
- los eventos de sistema (entradas/salidas) se separan del texto normal  
- es muy sencillo extender el protocolo (salas, autenticación, etc.)

### 2. Versión UDP – Difusión sin estado

**Servidor (UDP)**

- Utiliza `socket.AF_INET`, `SOCK_DGRAM` (UDP)
- Mantiene un `set` con las direcciones de clientes y un mapeo `(ip, port) -> alias`
- Cuando un cliente envía `__HELLO__`, el servidor:
  - registra la nueva conexión
  - reenvía (`broadcast`) el `__HELLO__` al resto de clientes
  - responde únicamente al cliente nuevo con `__USERS__`

**Cliente (UDP)**

- Ejecuta un **hilo receptor** para mantener la interfaz activa mientras escucha mensajes
- Usa códigos ANSI (sin librerías externas) para:
  - colores por usuario
  - mensajes de “sistema” (conexiones, desconexiones, avisos)
- Incluye comandos básicos:
  - `/clear` – limpiar pantalla
  - `/users` – mostrar usuarios conectados conocidos
  - `/quit` – salir correctamente (envía `__LEAVE__`)

> Esta versión es ideal para entender la comunicación **sin conexión (connectionless)**  
> y el comportamiento tipo *broadcast*.

---

### **3. Versión TCP – servidor multihilo**

**Servidor (TCP)**

- Utiliza `socket.AF_INET`, `SOCK_STREAM` (TCP)
- Por cada nueva conexión lanza un `threading.Thread` ejecutando `manejar_cliente`
- Lee línea a línea mediante `makefile("r")`
- La primera línea recibida de cada cliente es su **alias**
- Mantiene un diccionario `socket -> alias`
- Implementa un *broadcast simulado* a todos los clientes excepto el emisor  
  (unicast repetido, comunicación muchos-a-muchos)
- Libera recursos y notifica a otros con `__LEAVE__` al desconectar un cliente

### **Cliente (TCP)**

- Envía el alias como primera línea tras conectar
- Inicia un **hilo receptor** que:
  - lee líneas desde el servidor
  - analiza `[Alias] mensaje`
  - detecta eventos internos (`__HELLO__`, `__LEAVE__`, `__USERS__`)
  - reproduce sonido y muestra mensajes con color
- El hilo principal gestiona la entrada del usuario, las “burbujas” locales de mensaje y los comandos

> Esta versión refleja una arquitectura clásica de chat **TCP multihilo**,  
> compacta, clara y orientada a aprendizaje.


---

## 🖼 Material visual

### Captura del cliente en terminal

![Client UI screenshot](docs/captura_chat.png)

---

## ⏳ Requisitos

- **Python 3.8 o superior**
- No se requieren librerías externas
- Funciona en Windows / Linux / macOS

Opcional en Windows (para sonido personalizado):

```powershell
pip install winsound
```

*(En la mayoría de sistemas ya se utiliza la campanita ANSI `\a` por defecto.)*

---

## ▶ Cómo ejecutarlo

Se asume una estructura con algo como:

```text
udp_server.py
udp_client.py
tcp_server.py
tcp_client.py
```

### Modo UDP

**Servidor:**

```bash
python3 udp_server.py
```

**Cliente:**

```bash
python3 udp_client.py
```

El cliente pedirá:

```text
Server IP:
Alias:
```

---

### Modo TCP

**Servidor:**

```bash
python3 tcp_server.py
```

**Cliente:**

```bash
python3 tcp_client.py
```

De nuevo, el cliente solicitará:

```text
Server IP:
Alias:
```

---

## 💬 Comandos del cliente

| Comando | Acción                                               |
|---------|------------------------------------------------------|
| `/clear` | Limpia la pantalla                                  |
| `/users` | Muestra usuarios conectados (los que este conoce)   |
| `/quit`  | Sale del chat (TCP cierra, UDP envía LEAVE)         |

---

## 🚀 Ideas de mejora

| Función               | Valor                                         |
|-----------------------|-----------------------------------------------|
| Cifrado TLS/SSL       | Seguridad real en redes públicas              |
| Interfaz gráfica GUI  | Mejor experiencia de usuario                  |
| Sistema de login      | Identidad y permisos                          |
| Salas / canales       | Arquitectura escalable multi‑chat             |
| Historial de mensajes | Persistencia y registro para depuración       |
| Configuración por CLI | Puertos, host, colores, sonido, etc.          |

---

## 📁 Estructura de repositorio (sugerida)

```text
.
├── udp_server.py
├── udp_client.py
├── tcp_server.py
├── tcp_client.py
├── README.md
├── README_ES.md
└── docs/
    └── banner_pymultichat.png   # optional project banner
    └── captura_cliente.png      # client UI screenshot
```

---

## 🌍 Idiomas

- 🇬🇧 **Inglés** — [README.md](README.md) (recomendado como principal en GitHub)  
- 🇪🇸 **Español** — este archivo (`README_ES.md`)

---

## 📜 Licencia

El proyecto se publica bajo licencia **MIT**, ideal para proyectos de aprendizaje y portfolio.

---

⭐ Si te resulta útil o te gusta cómo está planteado, puedes dejarle una estrella en GitHub.
