# prediction_engine.py

# Importa um módulo simulado que representa o hardware PIM/CPU
from utils import SimulatedMLModel, CPU_CORE, PIM_UNIT 

class PredictionEngine:
    """
    Aplica o rigor de testes para a decisão de Offloading (PIM vs. CPU).
    """
    def __init__(self, ml_model: SimulatedMLModel, latency_threshold: float = 0.30, confidence_threshold: float = 0.999):
        # Regra de Rigor 1: Ganho mínimo de TTID para justificar o PIM (30%)
        self.MIN_TTID_GAIN = latency_threshold 
        # Regra de Rigor 2: Confiança mínima para evitar Falso Positivo (FP) Crítico (99.9%)
        self.MIN_CONFIDENCE = confidence_threshold 
        self.ml_model = ml_model 
        print("M2: PredictionEngine (ALP) inicializado.")

    def assess_and_decide(self, current_context: str, last_accesses: list) -> tuple:
        """Avalia se a tarefa deve ser enviada para PIM ou CPU."""
        
        if len(last_accesses) < 3:
            # Rigor: Não pode prever sem histórico de Stride mínimo.
            return 'CPU', [] 

        # 1. Previsão do ML_MODEL (Simulação)
        prediction_result = self.ml_model.predict(current_context, last_accesses)
        predicted_blocks = prediction_result.get('blocks', [])
        confidence = prediction_result.get('confidence', 0.0)
        predicted_ttid_pim = prediction_result.get('ttid_pim', 1.0)
        predicted_ttid_cpu = prediction_result.get('ttid_cpu', 1.0)
        
        # Garante divisão por zero (caso TTID seja 0)
        if predicted_ttid_cpu == 0:
            predicted_ttid_cpu = 1.0

        # 2. CHECAGEM DE RIGOR (CONFIANÇA)
        if confidence < self.MIN_CONFIDENCE:
            print(f"  [Decisão]: ALERTA: Confiança ({confidence:.4f}) abaixo de {self.MIN_CONFIDENCE}. FORÇANDO CPU (Segurança).")
            return 'CPU', []

        # 3. CHECAGEM DE RIGOR (GANHO DE TTID/ENERGIA)
        ttid_gain = 1 - (predicted_ttid_pim / predicted_ttid_cpu)
        if ttid_gain < self.MIN_TTID_GAIN:
            print(f"  [Decisão]: ALERTA: Ganho de TTID ({ttid_gain:.2%}) insuficiente. FORÇANDO CPU (Eficiência Energética).")
            return 'CPU', []
        
        # DECISÃO RIGOROSA: Passou em todos os testes.
        print(f"  [Decisão]: SUCESSO: Desvio para PIM (Ganho: {ttid_gain:.2%}, Confiança: {confidence:.4f}).")
        return 'PIM', predicted_blocks

    def execute_task(self, task_function, task_data, tracer):
        """Função unificada para executar a tarefa com base na decisão do OLP."""
        context, accesses = tracer.get_context_data()
        decision, blocks_to_prefetch = self.assess_and_decide(context, accesses)
        
        if decision == 'PIM':
            return PIM_UNIT.load_data_and_task(task_function, task_data, blocks_to_prefetch)
        else:
            return CPU_CORE.execute(task_function, task_data)

# # Nota: Você precisará criar o arquivo utils.py para rodar este módulo.