# Guía rápida: conectarse a Engram Cloud

---

## 0. PARAMETROS CONEXION

Pásale solo estos datos:

```text
TU_IP_VPS = 91.134.240.217
SERVER  = http://TU_IP_VPS:18080
PROJECT = mi-proyecto
TOKEN   = ENGRAM_CLOUD_TOKEN = b3be760d0dd38c9af65d44ecd52b4fed71463e295b90806b4dbd5809693beb2b
```
### Paso 1: comprobar que tiene Engram instalado

```powershell
engram version
```

Si no esta instalado, instalar Engram primero desde las releases del repo.

---

### Paso 2: configurar el servidor Cloud

```powershell
engram cloud config --server http://TU_IP_VPS:18080
```

Ejemplo:

```powershell
engram cloud config --server http://91.xxx.xxx.xxx:18080
```

---

### Paso 3: configurar el token

```powershell
$env:ENGRAM_CLOUD_TOKEN="TOKEN"
```

Nota: esta variable dura solo mientras esa terminal de PowerShell esté abierta. Si abre otra terminal, tendrá que volver a ponerla.

---

### Paso 4: enrollarse al proyecto

```powershell
engram cloud enroll mi-proyecto
```

El nombre del proyecto tiene que coincidir exactamente con el valor de:

```text
ENGRAM_CLOUD_ALLOWED_PROJECTS
```

---

### Paso 5: sincronizar contra la VPS

```powershell
engram sync --cloud --project mi-proyecto
```

Esto descarga/sube las memorias del proyecto compartido.

---

### Paso 6: buscar las memorias sincronizadas


```powershell
engram search "OVH"
```

O:

```powershell
engram search "TEST CLOUD OVH"
```

Si todo está bien, debería ver memorias como:

```text
TEST CLOUD OVH 001
Test OVH Jeremias
```
