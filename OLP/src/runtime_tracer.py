# runtime_tracer.py

class RuntimeTracer:
    """
    Rastreia o contexto de execução e os padrões de acesso à memória.
    Métrica de Entrada: Contexto da Aplicação + Padrão de Stride.
    """
    def __init__(self):
        # Armazena histórico: {'Contexto_ID': [acesso_1, acesso_2, ...]}
        self.history = {} 
        self.context_id = None
        print("M1: RuntimeTracer inicializado.")

    def set_context(self, function_name: str, line_number: int):
        """Define o contexto atual (o ponto exato do código que está sendo executado)."""
        self.context_id = f"{function_name}_{line_number}"
        if self.context_id not in self.history:
            self.history[self.context_id] = []
        print(f"  -> Contexto definido: {self.context_id}")

    def log_access(self, memory_address: int):
        """Registra um acesso à memória para análise de Stride."""
        if self.context_id:
            # Mantém apenas um número limitado de acessos recentes para eficiência
            if len(self.history[self.context_id]) >= 100:
                self.history[self.context_id].pop(0) 
            self.history[self.context_id].append(memory_address)

    def get_context_data(self) -> tuple:
        """Retorna o contexto e os últimos acessos para o Módulo de Decisão (ALP)."""
        return self.context_id, self.history.get(self.context_id, [])

# # Exemplo de uso (para testagem):
# TRACER = RuntimeTracer()
# TRACER.set_context("matrix_multiply", 54)
# TRACER.log_access(0x1000)
# TRACER.log_access(0x1008)
# print(TRACER.get_context_data())