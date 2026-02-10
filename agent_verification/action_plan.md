# PLAN DE ACCIÓN PARA LIMPIEZA DE AGENTES
# Generado: 2026-02-10 15:50:02

## PRIMERO: HACER BACKUP
# Ejecutar: .\cleanup_agents.ps1 simulate
# Esto mostrará qué se eliminará sin hacer cambios

## SEGUNDO: REVISAR AGENTES 'REVIEW'
# Estos archivos pueden ser útiles pero necesitan trabajo:

  - ESQUELETO_AGENTE (234 archivos):       agents/registry.py       agents/registry_backup.py       agents/compliance\auditmaster.py

## TERCERO: ELIMINAR LO INNECESARIO
# Estos archivos se pueden eliminar inmediatamente:

  - CLASE_VACIA (5 archivos)   - ARCHIVO_MINIMO (49 archivos)

## CUARTO: CONSOLIDAR AGENTES ACTIVOS
# Agentes listos para producción:

  - AGENTE_OPERATIVO (52 archivos):       ✅ agents/marketing\abtestingia.py       ✅ agents/marketing\abtestingimpactia.py       ✅ agents/marketing\attributionmodelia.py       ✅ agents/marketing\audiencesegmenteria.py       ✅ agents/marketing\budgetforecastia.py

## PASOS:
1. Ejecutar: .\cleanup_agents.ps1 simulate
2. Revisar la lista de archivos para eliminar
3. Ejecutar: .\cleanup_agents.ps1 cleanup (esto creará backup automático)
4. Mover archivos 'review' a carpeta separada para desarrollo futuro
5. Documentar los agentes operativos restantes
