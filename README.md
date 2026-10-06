maldev-educational-ransomware/
│
├── client/
│   ├── simulator.py
│   └── requirements.txt
│
├── server/
│   ├── server.py
│   └── requirements.txt
│
├── lab_files/
│   ├── example.txt
│   ├── example.pdf
│   ├── example.jpg
│   └── example.docx
│
├── README.md
├── LICENSE
└── .gitignore





# Educational Ransomware CTF

Laboratorio educativo para entrenamiento de equipos SOC y DFIR.

El proyecto simula el comportamiento visual y operativo de un incidente
de ransomware, pero está diseñado para ejecutarse de forma segura en un
sandbox o máquina de laboratorio.

## Características

- Simulación de ransomware.
- Creación de archivos señuelo.
- Artefactos `.locked`.
- Ransom note / interfaz de recuperación.
- Cuenta atrás de 8 horas.
- Challenge ID único.
- Comunicación únicamente con `localhost:8080`.
- Servidor Python para gestionar el CTF.
- Validación mediante RSA.
- No se cifran archivos reales.
- No se eliminan archivos reales.
- Los archivos originales permanecen intactos.

## Arquitectura

```text
+-----------------------+
|   Ransomware CTF      |
|       Client          |
+-----------+-----------+
            |
            | HTTP
            |
            v
+-----------------------+
|  Python CTF Server    |
|    localhost:8080     |
+-----------------------+

-------------------------------


             ┌───────────────────┐
             │     Simulator     │
             └─────────┬─────────┘
                       │
                       ▼
              Creates dummy files
                       │
                       ▼
              Fake "encrypting"
                       │
                       ▼
             NO REAL ENCRYPTION
                       │
                       ▼
                localhost:8080
                       │
                       ▼
                RSA CTF challenge
                       │
                       ▼
                8-hour countdown
                       │
                       ▼
                 Enter RSA key
                       │
              ┌────────┴────────┐
              │                 │
           Correct           Incorrect
              │                 │
              ▼                 ▼
          UNLOCKED         Continue CTF
