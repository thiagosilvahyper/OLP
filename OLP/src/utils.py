# utils.py - Simulações de Hardware e ML para desenvolvimento

# --- Simulação do Hardware ---
class CPUCore:
    def execute(self, task_function, data):
        print(f"  [CPU]: Executando {task_function.__name__}...")
        return "Resultado da CPU"
    
    def resume_execution(self, state):
        print(f"  [CPU]: Retomando execução a partir do estado {state}.")

class PIMUnit:
    def load_data_and_task(self, task_function, data, prefetch_blocks):
        print(f"  [PIM]: Descarregando {task_function.__name__} com {len(prefetch_blocks)} blocos de prefetch.")
        return "Resultado do PIM"
        
    def halt_execution(self):
        print("  [PIM]: Execução PARADA IMEDIATAMENTE (Halt).")
    
    def power_gate_partial(self):
        print("  [PIM]: Power Gating Parcial acionado.")

    def retrieve_state_at(self, checkpoint):
        # Simula a recuperação de dados
        return f"State_{checkpoint}"
        
CPU_CORE = CPUCore()
PIM_UNIT = PIMUnit()

# --- Simulação do Modelo ML (Para Módulo 2) ---
class SimulatedMLModel:
    """Simula o modelo ALP treinado para previsão."""
    
    def predict(self, context, accesses):
        """
        Simulação de resultado ideal (99.99% de confiança, 40% de ganho de TTID).
        """
        # Estes valores viriam do seu modelo de ML real
        
        # Simulação de um resultado ideal
        if "matrix_multiply" in context and len(accesses) > 10:
             return {
                'blocks': [0x1010, 0x1020, 0x1030], 
                'confidence': 0.9999,
                'ttid_pim': 100,
                'ttid_cpu': 160
            }
        
        # Simulação de um resultado de baixa confiança
        return {
            'blocks': [], 
            'confidence': 0.85, # Não atinge 0.999
            'ttid_pim': 100,
            'ttid_cpu': 110 # Ganho de apenas 9.09%
        }
    
ML_MODEL = SimulatedMLModel()