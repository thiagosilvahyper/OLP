# =================================================================
# OLP_API.py (Representação da Interface Central)
# =================================================================

# Importa as classes do OLP Core
from runtime_tracer import RuntimeTracer
from prediction_engine import PredictionEngine
from pim_recovery import PIMRecoveryModule
from rem_sync import REMSyncModule
from utils import ML_MODEL 

class OLPCoreAPI:
    """
    Interface de Programação para o Otimizador de Localidade Preditivo (OLP).
    Projetada para ser chamada por código de aplicação sensível à latência (ex: IA/Big Data).
    """
    
    def __init__(self):
        # 1. Inicialização dos Módulos Core
        self.tracer = RuntimeTracer()
        self.rem_sync = REMSyncModule()
        self.engine = PredictionEngine(ML_MODEL) # Passa o ML_MODEL simulado
        self.recovery = PIMRecoveryModule(self.engine, self.rem_sync)
        
        print("\n[OLP API]: Sistema pronto. Otimização Ativa.")

    def set_context(self, function_name: str, scope_id: int):
        """
        [CHAMADA OBRIGATÓRIA] Define o ponto do código que o OLP deve rastrear.
        Isso é crucial para o Módulo 1 (Tracer).
        
        Args:
            function_name: Nome da função ou método (ex: "training_loop_forward_pass").
            scope_id: ID única do escopo (ex: número da linha ou um hash).
        """
        self.tracer.set_context(function_name, scope_id)
        
    def execute_optimized(self, task_function: callable, task_data: list) -> any:
        """
        [CHAMADA PRINCIPAL] Executa uma tarefa, permitindo que o OLP decida 
        se deve ser desviada para PIM ou executada na CPU.
        
        O OLP-ALP fará aqui o teste de Confiança e Ganho de TTID.
        
        Args:
            task_function: A função de processamento a ser otimizada (ex: matrix_multiply).
            task_data: Os dados brutos a serem processados.
        
        Returns:
            Resultado da execução (do PIM ou da CPU).
        """
        # Módulo 2 é chamado para decisão e execução.
        result = self.engine.execute_task(task_function, task_data, self.tracer)
        
        # Módulo 1 é chamado para logar o acesso real (para feedback/re-treino)
        # Assumindo que a execução envolve acessos logados dentro da task_function
        
        return result

    def register_checkpoint(self, recovery_address: int):
        """
        [CHAMADA DE SEGURANÇA] Registra um ponto seguro para rollback em caso de FP crítico.
        Corresponde ao ponto de referência para o Módulo 3 (Recovery).
        
        Args:
            recovery_address: O endereço de memória do último estado de dados válido.
        """
        self.recovery.LAST_GOOD_CHECKPOINT = recovery_address
        print(f"[OLP API]: Checkpoint de recuperação registrado em {hex(recovery_address)}.")

    # A interrupção handle_critical_interrupt() do Módulo 3 é chamada pelo hardware/driver,
    # e não diretamente pelo desenvolvedor.