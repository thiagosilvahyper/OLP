# pim_recovery.py

# Importa módulos necessários
from prediction_engine import PredictionEngine
from rem_sync import REMSyncModule
from utils import PIM_UNIT, CPU_CORE

class PIMRecoveryModule:
    """
    Gerencia a mitigação de Falsos Positivos (FP) e o aprendizado em tempo real.
    """
    def __init__(self, decision_engine: PredictionEngine, rem_sync: REMSyncModule):
        self.DECISION_ENGINE = decision_engine
        self.REM_SYNCHRONIZER = rem_sync
        # Armazena o ponto de recuperação mais recente para rollback (Simulado)
        self.LAST_GOOD_CHECKPOINT = 0x0 
        print("M3: PIMRecoveryModule inicializado.")

    def handle_critical_interrupt(self, error_type: str, faulty_context: str):
        """
        Rotina chamada pelo hardware do PIM em caso de Prefetch Miss (FP Crítico).
        Esta rotina deve ter prioridade máxima.
        """
        
        # 1. PARADA IMEDIATA E ALERTA (RIGOR MÁXIMO)
        PIM_UNIT.halt_execution()
        
        # USO DO REM-Sync para garantir a menor latência de alerta à CPU
        self.REM_SYNCHRONIZER.send_critical_interrupt(error_type) 
        PIM_UNIT.power_gate_partial()  # Redução imediata de consumo na unidade PIM
        
        print(f"\n!!! FALHA CRÍTICA DETECTADA: {error_type} no Contexto {faulty_context} !!!")
        
        # 2. ROLLBACK E RE-EXECUÇÃO
        try:
            # Simulação: Recupera o estado da tarefa
            task_state = PIM_UNIT.retrieve_state_at(self.LAST_GOOD_CHECKPOINT)
            
            # Re-análise e Aprendizado
            self.update_ml_model_with_failure(faulty_context, task_state)
            
            # Retoma a tarefa na CPU (Caminho seguro)
            print(f"  -> Assumindo tarefa na CPU a partir do Checkpoint: {self.LAST_GOOD_CHECKPOINT}")
            CPU_CORE.resume_execution(task_state)
            
        except Exception as e:
            # Falha de Rollback: Loga e emite alerta final.
            print(f"ERRO FATAL NA RECUPERAÇÃO: {e}")
            self.log_and_shutdown_node()
            
        # 3. AJUSTE DE RIGOR PÓS-FALHA
        # Aumenta temporariamente o requisito de confiança para evitar FPs em cascata
        self.DECISION_ENGINE.MIN_CONFIDENCE = 0.99999 
        print(f"  -> Rigor aumentado: Confiança mínima agora é {self.DECISION_ENGINE.MIN_CONFIDENCE}")

    def update_ml_model_with_failure(self, context, state):
        """Simulação de treinamento em tempo real para evitar FPs futuros."""
        # Aqui, você enviaria os dados de (contexto, acesso real, erro) para o ML_MODEL
        # para que ele classifique esse padrão como 'Decisão Real: CPU'.
        print("  -> Logando Falha Crítica e Sinalizando Re-treinamento ALP.")
        
    def log_and_shutdown_node(self):
        # A última medida para garantir que a energia não seja desperdiçada continuamente.
        print("  -> Log de falha persistente e Desligamento do Nó afetado.")