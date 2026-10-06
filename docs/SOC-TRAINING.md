# SOC Training Guide

## Objective

This exercise simulates a ransomware incident in a controlled laboratory environment.

The simulator does NOT:

- Encrypt real files.
- Delete real files.
- Modify system files.
- Establish persistence.
- Perform privilege escalation.
- Communicate with external infrastructure.

Communication is restricted to the local training server.

## Initial Scenario

The analyst receives an alert indicating suspicious ransomware-like activity on a workstation.

The simulated malware:

1. Creates harmless training files.
2. Displays a simulated encryption process.
3. Contacts the local training server.
4. Starts an 8-hour simulated countdown.
5. Requests an RSA challenge key.
6. Allows the analyst to unlock the simulation by providing the correct key.

## SOC Investigation

The analyst should determine:

- Which process generated the activity.
- Which files were involved.
- When the activity started.
- Which network connection was established.
- Which local port was contacted.
- What information was exchanged with the server.
- Whether persistence was established.
- Whether files were actually modified.

## Expected Network Indicator

The simulator communicates with:

127.0.0.1:8080

No external network communication should be required.

## Expected Analyst Actions

The SOC analyst should:

1. Identify the suspicious process.
2. Isolate the laboratory host if required by the exercise.
3. Collect relevant process information.
4. Identify files created by the simulator.
5. Review local network connections.
6. Identify communication with port 8080.
7. Capture relevant logs.
8. Preserve evidence.
9. Determine that the file encryption is simulated.
10. Investigate the RSA challenge.
11. Recover the challenge key.
12. Unlock the simulation.

## Training Objective

The goal is not to recover encrypted production data.

The goal is to practice:

- Alert triage.
- Process investigation.
- File-system investigation.
- Network investigation.
- Evidence preservation.
- Incident documentation.
- Coordination between SOC and DFIR.
